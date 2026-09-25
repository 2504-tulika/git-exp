from src.config.database import SessionLocal
from src.config.settings import settings
from src.exceptions.exceptions import PolicyNotFoundError, UnauthorizedPolicyAccessError
from src.rag.retriever import retrieve_for_claim
from src.repositories.policy_repository import PolicyRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def check_policy_coverage(policy_id, customer_id, claim_type, incident_description, incident_date):
    """
    Return everything the agent needs to judge coverage for one claim: policy metadata, whether the claim falls inside the policy's active
    window, and the clauses most relevant to this claim type and description.

    Incident_date must be a python date object (not a string) -- the caller is responsible for parsing it first.

    Raises PolicyNotFoundError if policy_id doesn't exist at all, and UnauthorizedPolicyAccessError if it exists but customer_id isn't one
    of its policyholders. Existence is checked before ownership.
    """
    db = SessionLocal()
    try:
        repo = PolicyRepository(db)

        policy = repo.get_by_id(policy_id)
        if policy is None:
            raise PolicyNotFoundError(f"Policy {policy_id} not found")

        if not repo.customer_owns_policy(customer_id, policy_id):
            raise UnauthorizedPolicyAccessError(
                f"Customer {customer_id} does not hold policy {policy_id}"
            )

        within_coverage_period = policy.start_date <= incident_date <= policy.end_date

        relevant_clauses = retrieve_for_claim(
            claim_type=claim_type,
            incident_description=incident_description,
            policy_id=policy_id,
            top_k=settings.retrieval_top_k,
        )

        result = {
            "policy_id": policy.policy_id,
            "policy_type": policy.policy_type,
            "sub_type": policy.sub_type,
            "status": policy.status,
            "start_date": policy.start_date.isoformat(),
            "end_date": policy.end_date.isoformat(),
            "incident_date": incident_date.isoformat(),
            "within_coverage_period": within_coverage_period,
            "relevant_clauses": relevant_clauses,
        }
        logger.info(
            f"policy_tool: {policy_id} / {claim_type} -- "
            f"status={policy.status}, within_coverage_period={within_coverage_period}, "
            f"{len(relevant_clauses)} clause(s) retrieved"
        )
        return result
    finally:
        db.close()
