import re
from datetime import timedelta

from src.config.database import SessionLocal
from src.mcp.tools.claim_history_tool import serialize_claim
from src.repositories.claims_repository import ClaimsRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)

FREQUENT_CLAIMS_THRESHOLD = 3
CLUSTER_WINDOW_DAYS = 7
LATE_INTIMATION_THRESHOLD_DAYS = 15
AMOUNT_OUTLIER_RATIO = 3.0

_AMOUNT_PATTERN = re.compile(r"[\d,]+\.?\d*")


def _parse_amount(amount_text):
    """
    Extract a float from a claim_amount string. Returns None if the string is empty or has no parseable number -- callers must handle that, not
    assume every claim_amount is usable.
    """
    parsed_amount = None
    if amount_text:
        match = _AMOUNT_PATTERN.search(amount_text)
        if match:
            digits_only = match.group().replace(",", "")
            parsed_amount = float(digits_only)
    return parsed_amount


def assess_fraud_risk(customer_id, policy_id, incident_date, intimation_date, claim_amount=None, exclude_claim_id=None):
    """
    Return every fraud-risk signal we can check for this claim. Always
    succeeds (no exceptions raised for "risky" data -- risk signals are
    the whole point of this tool's output, not a reason to fail).
    """
    db = SessionLocal()
    try:
        repo = ClaimsRepository(db)

        prior_fraud_flag = repo.has_prior_fraud_flag(customer_id)

        total_claims = repo.count_claims_for_customer(customer_id)
        frequent_claimant = total_claims >= FREQUENT_CLAIMS_THRESHOLD

        nearby_claims = repo.get_claims_within_days_for_policy(
            policy_id, incident_date, CLUSTER_WINDOW_DAYS, exclude_claim_id=exclude_claim_id
        )
        clustered_claims = [serialize_claim(c) for c in nearby_claims]

        days_late = (intimation_date - incident_date).days
        late_intimation = days_late >= LATE_INTIMATION_THRESHOLD_DAYS

        amount_outlier = False
        customer_average_amount = None
        this_claim_amount = _parse_amount(claim_amount)
        if this_claim_amount is not None:
            past_claims = repo.get_claims_for_customer(customer_id)
            past_amounts = [
                a for a in (_parse_amount(c.claim_amount) for c in past_claims) if a is not None
            ]
            if past_amounts:
                customer_average_amount = sum(past_amounts) / len(past_amounts)
                if customer_average_amount > 0:
                    amount_outlier = (this_claim_amount / customer_average_amount) >= AMOUNT_OUTLIER_RATIO

        risk_signals = []
        if prior_fraud_flag:
            risk_signals.append("Customer has a prior claim flagged as fraud risk.")
        if frequent_claimant:
            risk_signals.append(f"Customer has filed {total_claims} claims in total (frequent claimant).")
        if len(clustered_claims) > 0:
            risk_signals.append(
                f"{len(clustered_claims)} other claim(s) on this same policy within "
                f"{CLUSTER_WINDOW_DAYS} days of this incident."
            )
        if late_intimation:
            risk_signals.append(
                f"Claim intimated {days_late} days after the incident "
                f"(policy treats {LATE_INTIMATION_THRESHOLD_DAYS}+ days as a fraud-risk indicator)."
            )
        if amount_outlier:
            risk_signals.append(
                f"Claim amount is {this_claim_amount / customer_average_amount:.1f}x this "
                f"customer's historical average claim amount."
            )

        result = {
            "customer_id": customer_id,
            "policy_id": policy_id,
            "prior_fraud_flag": prior_fraud_flag,
            "total_claims_by_customer": total_claims,
            "frequent_claimant": frequent_claimant,
            "clustered_claims": clustered_claims,
            "days_late": days_late,
            "late_intimation": late_intimation,
            "this_claim_amount": this_claim_amount,
            "customer_average_amount": customer_average_amount,
            "amount_outlier": amount_outlier,
            "risk_signals": risk_signals,
        }
        logger.info(
            f"fraud_risk_tool: customer={customer_id} policy={policy_id} -- "
            f"{len(risk_signals)} risk signal(s): {risk_signals}"
        )
        return result
    finally:
        db.close()
