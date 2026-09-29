from src.config.database import SessionLocal
from src.exceptions.exceptions import (
    CustomerNotFoundError,
    PolicyNotFoundError,
    UnauthorizedPolicyAccessError,
)
from src.repositories.claims_repository import ClaimsRepository
from src.repositories.customer_repository import CustomerRepository
from src.repositories.policy_repository import PolicyRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def serialize_claim(claim):
    """Turn one ClaimsHistory ORM row into a plain dict the agent/JSON layer can use."""
    serialized = {
        "claim_id": claim.claim_id,
        "policy_id": claim.policy_id,
        "customer_id": claim.customer_id,
        "claim_type": claim.claim_type,
        "incident_date": claim.incident_date.isoformat(),
        "intimation_date": claim.intimation_date.isoformat(),
        "claim_amount": claim.claim_amount,
        "status": claim.status,
        "fraud_flag": claim.fraud_flag,
    }
    return serialized


def get_claim_history(customer_id, policy_id=None):
    """
    Return this customer's claim history: every past claim across all their policies, plus a flag for whether any of those claims were
    fraud-flagged. If policy_id is given, also return this customer's claims on just that policy.

    All checks happen BEFORE any claim data is read:
      - the customer must exist (CustomerNotFoundError)
      - if policy_id is given, the policy must exist (PolicyNotFoundError) and this customer must actually hold it (UnauthorizedPolicyAccessError)

    """
    db = SessionLocal()
    try:
        customer_repo = CustomerRepository(db)
        policy_repo = PolicyRepository(db)
        claims_repo = ClaimsRepository(db)

        if customer_repo.get_by_id(customer_id) is None:
            raise CustomerNotFoundError(f"Customer {customer_id} not found")

        if policy_id is not None:
            if policy_repo.get_by_id(policy_id) is None:
                raise PolicyNotFoundError(f"Policy {policy_id} not found")
            if not policy_repo.customer_owns_policy(customer_id, policy_id):
                raise UnauthorizedPolicyAccessError(
                    f"Customer {customer_id} does not hold policy {policy_id}"
                )

        all_claims = claims_repo.get_claims_for_customer(customer_id)
        serialized_all = [serialize_claim(c) for c in all_claims]

        serialized_for_policy = None
        if policy_id is not None:
            policy_claims = claims_repo.get_claims_for_policy(policy_id)
            own_policy_claims = [c for c in policy_claims if c.customer_id == customer_id]
            serialized_for_policy = [serialize_claim(c) for c in own_policy_claims]

        result = {
            "customer_id": customer_id,
            "total_claims_by_customer": len(serialized_all),
            "has_prior_fraud_flag": claims_repo.has_prior_fraud_flag(customer_id),
            "claims_by_customer": serialized_all,
            "policy_id": policy_id,
            "claims_for_policy": serialized_for_policy,
        }
        logger.info(
            f"claim_history_tool: customer={customer_id} -- "
            f"{len(serialized_all)} total claim(s), "
            f"has_prior_fraud_flag={result['has_prior_fraud_flag']}"
        )
        return result
    finally:
        db.close()

