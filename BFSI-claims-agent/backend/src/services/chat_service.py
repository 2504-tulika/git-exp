from src.agents.chat_agent import send_chat_message
from src.exceptions.exceptions import ChatNotAvailableError
from src.services.claim_service import get_claim_detail
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _build_claim_context(claim):
    """
    Turn one claim into the plain-text block the chat agent sees as its
    system message. Everything here belongs to the customer who owns the
    claim (checked by get_claim_detail before this runs), so there is
    nothing here that needs hiding from them.
    """
    lines = [
        f"Policy: {claim.policy_id}",
        f"Claim type: {claim.claim_type}",
        f"Incident date: {claim.incident_date}",
        f"Incident description: {claim.incident_description}",
        f"Claimed amount: {claim.claim_amount or 'not specified'}",
        f"Claim status: {claim.status}",
        f"AI recommendation: {claim.ai_recommendation}",
        f"AI rationale: {claim.ai_rationale}",
    ]
    return "\n".join(lines)


def send_message(db, current_user, claim_id, user_message):
    """
    Handle one chat message from the logged-in customer about one of
    their own claims.

    Reuses get_claim_detail for the ownership check -- a claim_id that
    doesn't exist, or belongs to someone else, is rejected exactly the
    same way here as everywhere else in the app.
    """
    claim = get_claim_detail(db, current_user, claim_id)

    if claim.ai_recommendation is None:
        raise ChatNotAvailableError(
            f"Claim {claim_id} does not have an AI recommendation to discuss yet."
        )

    claim_context = _build_claim_context(claim)
    thread_id = f"{current_user.customer_id}:{claim_id}"

    reply = send_chat_message(thread_id, claim_context, user_message)
    logger.info(f"Chat message handled for claim {claim_id} (customer {current_user.customer_id})")
    return reply