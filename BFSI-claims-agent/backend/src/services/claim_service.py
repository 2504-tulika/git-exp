import uuid
from datetime import date

from src.agents.claims_agent import process_claim_async
from src.exceptions.exceptions import ClaimNotFoundError, UnauthorizedPolicyAccessError
from src.mcp.tools.fraud_risk_tool import assess_fraud_risk
from src.repositories.claims_repository import ClaimsRepository
from src.repositories.policy_repository import PolicyRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _generate_claim_id():
    """
    New claim_ids follow the same "CLM-" prefix as the seeded historical data, suffixed with random hex rather than a sequential number -- so
    a new claim can never collide with the 30 seeded claim_ids.
    """
    suffix = uuid.uuid4().hex[:8].upper()
    claim_id = f"CLM-{suffix}"
    return claim_id


def _format_claim_amount(claim_amount):
    """Format a plain number into the same text style already stored in claims_history, e.g. "Rs. 45,000"."""
    formatted_amount = None
    if claim_amount is not None:
        formatted_amount = f"Rs. {claim_amount:,.0f}"
    return formatted_amount


async def submit_claim(db, current_user, request):
    """
    Submit a new claim for the logged-in customer.
    """
    policy_repo = PolicyRepository(db)
    claims_repo = ClaimsRepository(db)

    if not policy_repo.customer_owns_policy(current_user.customer_id, request.policy_id):
        logger.warning(
            f"Blocked claim submission: customer {current_user.customer_id} "
            f"does not hold policy {request.policy_id}"
        )
        raise UnauthorizedPolicyAccessError(
            f"Customer {current_user.customer_id} does not hold policy {request.policy_id}"
        )

    intimation_date = date.today()
    formatted_amount = _format_claim_amount(request.claim_amount)

    fraud_result = assess_fraud_risk(
        customer_id=current_user.customer_id,
        policy_id=request.policy_id,
        incident_date=request.incident_date,
        intimation_date=intimation_date,
        claim_amount=formatted_amount,
    )
    fraud_flag = len(fraud_result["risk_signals"]) > 0

    agent_claim = {
        "policy_id": request.policy_id,
        "customer_id": current_user.customer_id,
        "claim_type": request.claim_type,
        "incident_description": request.incident_description,
        "incident_date": request.incident_date.isoformat(),
        "intimation_date": intimation_date.isoformat(),
        "claim_amount": formatted_amount,
    }

    logger.info(
        f"Submitting claim: customer_id={current_user.customer_id}, "
        f"policy_id={request.policy_id}, claim_type={request.claim_type}, "
        f"fraud_flag={fraud_flag}"
    )

    try:
        agent_result = await process_claim_async(agent_claim)
        ai_recommendation = agent_result["recommendation"]
        ai_rationale = agent_result["rationale"]
    except Exception as exc:
        logger.error(
            f"Agent processing failed for customer_id={current_user.customer_id}, "
            f"policy_id={request.policy_id} -- recording claim anyway: {exc}"
        )
        ai_recommendation = "needs_more_info"
        ai_rationale = (
            "Automated review could not be completed due to a system error. "
            "This claim requires manual review."
        )

    claim = claims_repo.create_claim(
        claim_id=_generate_claim_id(),
        policy_id=request.policy_id,
        customer_id=current_user.customer_id,
        claim_type=request.claim_type,
        incident_date=request.incident_date,
        incident_description=request.incident_description,
        intimation_date=intimation_date,
        claim_amount=formatted_amount,
        status="Under Review",
        fraud_flag=fraud_flag,
        ai_recommendation=ai_recommendation,
        ai_rationale=ai_rationale,
    )

    logger.info(f"Claim {claim.claim_id} recorded: ai_recommendation={ai_recommendation}")
    return claim


def get_my_claims(db, current_user):
    """Every claim filed by the logged-in customer."""
    claims_repo = ClaimsRepository(db)
    claims = claims_repo.get_claims_for_customer(current_user.customer_id)
    return claims


def get_claim_detail(db, current_user, claim_id):
    """
    One specific claim, only if it belongs to the logged-in customer.
    Existence is checked first -- same reasoning as policy_coverage_tool: reporting "unauthorized" for a claim_id that's simply wrong would be misleading.
    """
    claims_repo = ClaimsRepository(db)
    claim = claims_repo.get_by_id(claim_id)

    if claim is None:
        raise ClaimNotFoundError(f"Claim {claim_id} not found")

    if claim.customer_id != current_user.customer_id:
        raise UnauthorizedPolicyAccessError(
            f"Claim {claim_id} does not belong to customer {current_user.customer_id}"
        )

    return claim


