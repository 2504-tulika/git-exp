import uuid
from datetime import date

from src.agents.claims_agent import review_claim_events
from src.config import constants
from src.config.database import SessionLocal
from src.exceptions.exceptions import (
    ClaimLimitExceededError,
    ClaimNotFoundError,
    UnauthorizedPolicyAccessError,
)
from src.mcp.tools.fraud_risk_tool import assess_fraud_risk
from src.repositories.claims_repository import ClaimsRepository
from src.repositories.policy_repository import PolicyRepository
from src.utils.guardrails import check_rate_limit, collect_allowed_ids, enforce_decision_rules, guard_text
from src.utils.logger import get_logger
from src.utils.pii import mask_pii
from src.utils.validators import find_injection_patterns

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


def prepare_claim(db, current_user, request):
    """
    Everything that must happen BEFORE the AI review, in order (cheap and
    strict first, expensive last):
      1. the customer must hold the policy
      2. the per-customer rate limit must not be hit
      3. injection scan, then PII masking, of the claim text
      4. the yearly claim limit must not be reached
      5. the deterministic fraud-risk check

    Any problem is raised here as a normal exception, so a caller can turn
    it into a proper HTTP error before a response (or a stream) has started.
    Returns a plain dict ("ctx") for review_and_save_claim -- plain values
    only, so it stays valid after this request's database session closes.
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

    check_rate_limit(
        f"claim:{current_user.customer_id}",
        constants.CLAIM_RATE_LIMIT_MAX_SUBMISSIONS,
        constants.CLAIM_RATE_LIMIT_WINDOW_SECONDS,
        constants.CLAIM_RATE_LIMITED,
    )

    # Scan the raw text for injection attempts, then hide any sensitive details
    # BEFORE anything is saved or sent to the model.
    injection_flagged = bool(
        find_injection_patterns(request.incident_description) or find_injection_patterns(request.claim_type)
    )
    claim_type, claim_type_pii = mask_pii(request.claim_type)
    incident_description, description_pii = mask_pii(request.incident_description)
    pii_found = sorted(set(claim_type_pii + description_pii))
    if pii_found:
        logger.warning(f"GUARDRAIL PII masked in claim text for customer {current_user.customer_id}: {pii_found}")

    incident_year = request.incident_date.year
    claims_this_year = claims_repo.count_claims_for_customer_on_policy_in_year(
        current_user.customer_id, request.policy_id, incident_year
    )
    if claims_this_year >= constants.MAX_CLAIMS_PER_POLICY_PER_YEAR:
        logger.warning(
            f"Blocked claim submission: customer {current_user.customer_id} already has "
            f"{claims_this_year} claim(s) on policy {request.policy_id} for {incident_year}"
        )
        raise ClaimLimitExceededError(
            constants.CLAIM_LIMIT_REACHED.format(
                limit=constants.MAX_CLAIMS_PER_POLICY_PER_YEAR,
                policy_id=request.policy_id,
                year=incident_year,
            )
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
    fraud_flag = len(fraud_result["claim_signals"]) > 0

    agent_claim = {
        "policy_id": request.policy_id,
        "customer_id": current_user.customer_id,
        "claim_type": claim_type,
        "incident_description": incident_description,
        "incident_date": request.incident_date.isoformat(),
        "intimation_date": intimation_date.isoformat(),
        "claim_amount": formatted_amount,
    }

    logger.info(
        f"Submitting claim: customer_id={current_user.customer_id}, "
        f"policy_id={request.policy_id}, claim_type={claim_type}, "
        f"fraud_flag={fraud_flag}"
    )

    return {
        "customer_id": current_user.customer_id,
        "policy_id": request.policy_id,
        "claim_type": claim_type,
        "incident_date": request.incident_date,
        "incident_description": incident_description,
        "intimation_date": intimation_date,
        "claim_amount": formatted_amount,
        "injection_flagged": injection_flagged,
        "pii_found": pii_found,
        "fraud_result": fraud_result,
        "fraud_flag": fraud_flag,
        "agent_claim": agent_claim,
    }


async def review_and_save_claim(db, ctx):
    """
    The AI review, the safety checks on its output, and saving the claim.
    An async generator that yields progress events as it goes:

        {"type": "step", "step": <name>, "status": "running" | "done"}   (several)
        {"type": "final", "claim": <saved ClaimsHistory row>}            (last)

    The model's own text is deliberately NOT streamed to the customer:
    the decision rules and output scrubbing run after the model finishes
    and can change the recommendation or the wording, so the customer only
    ever sees the result that has been through them.

    If the review fails for any reason, the claim is still saved as
    needs_more_info for manual review -- a claim is never lost because the
    AI was unavailable.
    """
    policy_repo = PolicyRepository(db)
    claims_repo = ClaimsRepository(db)
    customer_id = ctx["customer_id"]
    policy_id = ctx["policy_id"]

    try:
        result = None
        async for event in review_claim_events(ctx["agent_claim"], ctx["fraud_result"]):
            if event["type"] == "step":
                yield event
            else:
                result = event["result"]

        yield {"type": "step", "step": "safety", "status": "running"}
        ai_recommendation, ai_rationale = enforce_decision_rules(
            recommendation=result["recommendation"],
            rationale=result["rationale"],
            policy=policy_repo.get_by_id(policy_id),
            incident_date=ctx["incident_date"],
            claim_signals=ctx["fraud_result"]["claim_signals"],
            tools_called={call["tool"] for call in result.get("tool_calls", [])},
            injection_flagged=ctx["injection_flagged"],
        )
        ai_rationale = guard_text(ai_rationale, collect_allowed_ids(db, customer_id))
        yield {"type": "step", "step": "safety", "status": "done"}
    except Exception as exc:
        logger.error(
            f"Agent processing failed for customer_id={customer_id}, "
            f"policy_id={policy_id} -- recording claim anyway: {exc}"
        )
        ai_recommendation = "needs_more_info"
        ai_rationale = (
            "Automated review could not be completed due to a system error. "
            "This claim requires manual review."
        )

    claim = claims_repo.create_claim(
        claim_id=_generate_claim_id(),
        policy_id=policy_id,
        customer_id=customer_id,
        claim_type=ctx["claim_type"],
        incident_date=ctx["incident_date"],
        incident_description=ctx["incident_description"],
        intimation_date=ctx["intimation_date"],
        claim_amount=ctx["claim_amount"],
        status="Under Review",
        fraud_flag=ctx["fraud_flag"],
        ai_recommendation=ai_recommendation,
        ai_rationale=ai_rationale,
    )

    logger.info(f"Claim {claim.claim_id} recorded: ai_recommendation={ai_recommendation}")
    claim.privacy_notice = constants.PII_NOTICE if ctx["pii_found"] else None
    yield {"type": "final", "claim": claim}


async def submit_claim(db, current_user, request):
    """Submit a new claim for the logged-in customer and return the saved claim."""
    ctx = prepare_claim(db, current_user, request)
    claim = None
    async for event in review_and_save_claim(db, ctx):
        if event["type"] == "final":
            claim = event["claim"]
    return claim


async def stream_submit_claim(ctx):
    """
    Same review as submit_claim, as a stream of progress events ending in
    the saved claim. Opens its OWN database session: the request's session
    (from get_db) can already be closed by the time a streamed response
    starts running.
    """
    db = SessionLocal()
    try:
        async for event in review_and_save_claim(db, ctx):
            yield event
    finally:
        db.close()


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