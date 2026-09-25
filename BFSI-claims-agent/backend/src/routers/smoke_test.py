import sys
from datetime import datetime
from pathlib import Path

import jwt
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.database import SessionLocal
from src.config.settings import settings
from src.exceptions.exceptions import register_exception_handlers
from src.repositories.user_repository import UserRepository
from src.routers.auth_router import router as auth_router
from src.utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TEST_USERNAME = "smoketest_user"
TEST_CUSTOMER_ID = "CUST-005"       
OTHER_CUSTOMER_ID = "CUST-006"     


def _cleanup():
    """Delete the test account if a previous run left it behind."""
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        existing = repo.get_by_username(TEST_USERNAME)
        if existing is not None:
            repo.delete(existing.id)
            logger.info(f"Cleaned up leftover test user '{TEST_USERNAME}' from a previous run")
    finally:
        db.close()


def run():
    lines = [f"# auth smoke test -- {datetime.now().isoformat(timespec='seconds')}", ""]
    all_passed = True

    _cleanup()

    app = FastAPI()
    app.include_router(auth_router)
    register_exception_handlers(app)
    client = TestClient(app)

    def check(label, condition, response):
        nonlocal all_passed
        all_passed = all_passed and condition
        status = "PASS" if condition else "FAIL"
        logger.info(f"[{status}] {label} -- HTTP {response.status_code}")
        lines.append(f"### [{status}] {label}")
        lines.append(f"- status: {response.status_code}")
        lines.append(f"- body: {response.json()}")
        lines.append("")

    # -- Signup: success --
    resp = client.post("/auth/signup", json={
        "customer_id": TEST_CUSTOMER_ID, "username": TEST_USERNAME, "password": "Passw0rd1",
    })
    check("Signup succeeds for a fresh customer_id", resp.status_code == 201, resp)

    # -- Signup: same customer_id again -> CustomerAlreadyRegisteredError (409) --
    resp = client.post("/auth/signup", json={
        "customer_id": TEST_CUSTOMER_ID, "username": "someoneelse", "password": "Passw0rd2",
    })
    check("Duplicate customer_id is rejected (409)", resp.status_code == 409, resp)

    # -- Signup: same username, different customer_id -> UsernameTakenError (409) --
    resp = client.post("/auth/signup", json={
        "customer_id": OTHER_CUSTOMER_ID, "username": TEST_USERNAME, "password": "Passw0rd3",
    })
    check("Duplicate username is rejected (409)", resp.status_code == 409, resp)

    # -- Signup: nonexistent customer_id -> CustomerNotFoundError (404) --
    resp = client.post("/auth/signup", json={
        "customer_id": "CUST-9999", "username": "brandnewuser", "password": "Passw0rd4",
    })
    check("Nonexistent customer_id is rejected (404)", resp.status_code == 404, resp)

    # -- Signup: weak password (schema validation, 422 before service even runs) --
    resp = client.post("/auth/signup", json={
        "customer_id": "CUST-007", "username": "weakpassuser", "password": "alllettersnodigits",
    })
    check("Weak password fails schema validation (422)", resp.status_code == 422, resp)

    # -- Login: correct credentials --
    resp = client.post("/auth/login", json={"username": TEST_USERNAME, "password": "Passw0rd1"})
    login_ok = resp.status_code == 200 and "access_token" in resp.json()
    check("Login succeeds with correct credentials", login_ok, resp)

    if login_ok:
        token = resp.json()["access_token"]
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        claims_ok = payload.get("sub") == TEST_USERNAME and payload.get("customer_id") == TEST_CUSTOMER_ID
        all_passed = all_passed and claims_ok
        logger.info(f"[{'PASS' if claims_ok else 'FAIL'}] Token carries correct sub/customer_id claims")
        lines.append(f"### [{'PASS' if claims_ok else 'FAIL'}] Token claims")
        lines.append(f"- payload: {payload}")
        lines.append("")

    # -- Login: wrong password --
    resp = client.post("/auth/login", json={"username": TEST_USERNAME, "password": "wrongpassword"})
    wrong_pw_detail = resp.json().get("detail")
    check("Wrong password is rejected (401)", resp.status_code == 401, resp)

    # -- Login: unknown username --
    resp = client.post("/auth/login", json={"username": "nosuchuser", "password": "whatever123"})
    unknown_user_detail = resp.json().get("detail")
    check("Unknown username is rejected (401)", resp.status_code == 401, resp)

    # -- No username enumeration: both failures return the exact same message --
    no_enumeration = wrong_pw_detail == unknown_user_detail
    all_passed = all_passed and no_enumeration
    logger.info(f"[{'PASS' if no_enumeration else 'FAIL'}] Wrong-password and unknown-username return identical messages (no enumeration)")
    lines.append(f"### [{'PASS' if no_enumeration else 'FAIL'}] No username enumeration")
    lines.append(f"- wrong-password detail: {wrong_pw_detail!r}")
    lines.append(f"- unknown-username detail: {unknown_user_detail!r}")
    lines.append("")

    _cleanup()

    lines.insert(2, f"## Overall: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED -- see above'}\n")

    report_dir = PROJECT_ROOT / "test_results"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"auth_smoke_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Report saved to {report_path}")

    return all_passed


if __name__ == "__main__":
    passed = run()
    sys.exit(0 if passed else 1)


