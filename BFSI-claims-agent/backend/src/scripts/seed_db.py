import argparse
import csv
from datetime import datetime
from pathlib import Path

from src.config.database import Base, engine, SessionLocal
from src.repositories.claims_repository import ClaimsRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.models import PolicyCustomer
from src.repositories.policy_repository import PolicyRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"

CLAIMS_CSV = "claims_history.csv"


def parse_date(date_str):
    """Our CSVs store dates like '08-Jan-1988' -- turn that into a real date."""
    return datetime.strptime(date_str, "%d-%b-%Y").date()


def read_csv(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def seed_customers(db):
    repo = CustomerRepository(db)
    if repo.get_all():
        logger.info("customers already seeded, skipping")
        return
    for row in read_csv("customers.csv"):
        repo.create(
            customer_id=row["customer_id"],
            name=row["name"],
            dob=parse_date(row["dob"]),
            gender=row["gender"],
            contact_number=row["contact_number"],
        )
    logger.info(f"Seeded {len(repo.get_all())} customers")


def seed_policies(db):
    repo = PolicyRepository(db)
    if repo.get_all():
        logger.info("policies already seeded, skipping")
        return
    for row in read_csv("policies.csv"):
        repo.create(
            policy_id=row["policy_id"],
            policy_type=row["policy_type"],
            sub_type=row["sub_type"],
            status=row["status"],
            start_date=parse_date(row["start_date"]),
            end_date=parse_date(row["end_date"]),
            premium=row["premium"],
            policy_document=row["policy_document"],
        )
    logger.info(f"Seeded {len(repo.get_all())} policies")


def seed_policy_customers(db):
    if db.query(PolicyCustomer).first() is not None:
        logger.info("policy_customers already seeded, skipping")
        return
    for row in read_csv("policy_customers.csv"):
        db.add(PolicyCustomer(policy_id=row["policy_id"], customer_id=row["customer_id"]))
    db.commit()
    logger.info(f"Seeded {db.query(PolicyCustomer).count()} policy-customer links")


def seed_claims(db):
    repo = ClaimsRepository(db)
    if repo.get_all():
        logger.info("claims already seeded, skipping")
        return
    for row in read_csv(CLAIMS_CSV):
        repo.create_claim(
            claim_id=row["claim_id"],
            policy_id=row["policy_id"],
            customer_id=row["customer_id"],
            claim_type=row["claim_type"],
            incident_date=parse_date(row["incident_date"]),
            incident_description=row.get("incident_description", ""),
            intimation_date=parse_date(row["intimation_date"]),
            claim_amount=row["claim_amount"],
            status=row["status"],
            fraud_flag=(row["fraud_flag"] == "Y"),
        )
    logger.info(f"Seeded {len(repo.get_all())} claims")


def run(reset=False):
    if reset:
        Base.metadata.drop_all(engine)
        logger.info("Dropped all tables (--reset)")

    Base.metadata.create_all(engine)
    logger.info("All tables created (or already existed)")

    db = SessionLocal()
    try:
        
        seed_customers(db)
        seed_policies(db)
        seed_policy_customers(db)
        seed_claims(db)
        logger.info("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Drop all tables before seeding")
    args = parser.parse_args()
    run(reset=args.reset)

