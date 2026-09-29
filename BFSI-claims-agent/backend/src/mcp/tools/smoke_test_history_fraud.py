import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from src.mcp.tools.claim_history_tool import get_claim_history
from src.mcp.tools.fraud_risk_tool import assess_fraud_risk
from src.utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[4]


def run():
    lines = [f"# claim_history / fraud_risk smoke test -- {datetime.now().isoformat(timespec='seconds')}", ""]
    all_passed = True

    lines.append("## claim_history_tool\n")

    history = get_claim_history("CUST-003", policy_id="MSI-MOT-1004")

    passed = history["total_claims_by_customer"] > 0 and history["claims_for_policy"] is not None
    all_passed = all_passed and passed
    logger.info(f"[{'PASS' if passed else 'FAIL'}] get_claim_history for CUST-003 / MSI-MOT-1004")
    lines.append(f"### [{'PASS' if passed else 'FAIL'}] Customer + policy history")
    lines.append(f"- total_claims_by_customer: {history['total_claims_by_customer']}")
    lines.append(f"- has_prior_fraud_flag: {history['has_prior_fraud_flag']}")
    lines.append(f"- claims_for_policy count: {len(history['claims_for_policy'])}")
    lines.append("")


    lines.append("## fraud_risk_tool\n")

    clustered = assess_fraud_risk(
        customer_id="CUST-003",
        policy_id="MSI-MOT-1004",
        incident_date=date(2026, 9, 16),  # inside the CLM-0010/0011 week
        intimation_date=date(2026, 9, 17),
    )
    passed = len(clustered["clustered_claims"]) >= 1
    all_passed = all_passed and passed
    logger.info(f"[{'PASS' if passed else 'FAIL'}] clustered_claims signal fires near CLM-0010/CLM-0011")
    lines.append(f"### [{'PASS' if passed else 'FAIL'}] Clustered claims signal")
    lines.append(f"- clustered_claims found: {len(clustered['clustered_claims'])}")
    lines.append(f"- risk_signals: {clustered['risk_signals']}")
    lines.append("")

    late = assess_fraud_risk(
        customer_id="CUST-003",
        policy_id="MSI-MOT-1002",
        incident_date=date(2026, 8, 20),
        intimation_date=date(2026, 8, 20) + timedelta(days=20),  # matches CLM-0006's 20-day gap
    )
    passed = late["late_intimation"] is True and late["days_late"] == 20
    all_passed = all_passed and passed
    logger.info(f"[{'PASS' if passed else 'FAIL'}] late_intimation signal fires at 20 days")
    lines.append(f"### [{'PASS' if passed else 'FAIL'}] Late intimation signal")
    lines.append(f"- days_late: {late['days_late']}")
    lines.append(f"- risk_signals: {late['risk_signals']}")
    lines.append("")

    clean = assess_fraud_risk(
        customer_id="CUST-004",
        policy_id="MSI-MOT-1003",
        incident_date=date(2026, 6, 1),
        intimation_date=date(2026, 6, 2),
    )
    passed = len(clean["risk_signals"]) == 0
    all_passed = all_passed and passed
    logger.info(f"[{'PASS' if passed else 'FAIL'}] clean claim raises no risk signals")
    lines.append(f"### [{'PASS' if passed else 'FAIL'}] Clean claim (no signals expected)")
    lines.append(f"- risk_signals: {clean['risk_signals']}")
    lines.append("")

    lines.append(f"## Overall: {'ALL CHECKS PASSED' if all_passed else 'SOME CHECKS FAILED -- see above'}")

    report_dir = PROJECT_ROOT / "test_results"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"history_fraud_smoke_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Report saved to {report_path}")

    return all_passed


if __name__ == "__main__":
    passed = run()
    sys.exit(0 if passed else 1)

