from src.agents.chat_agent import get_chat_history, send_claim_chat_message, send_policies_chat_message
from src.config import constants
from src.config.settings import settings
from src.exceptions.exceptions import ChatNotAvailableError, RateLimitExceededError
from src.repositories.customer_repository import CustomerRepository
from src.services.claim_service import get_claim_detail
from src.utils.guardrails import check_rate_limit, collect_allowed_ids, guard_chat_reply
from src.utils.logger import get_logger
from src.utils.pii import mask_pii
from src.utils.validators import find_injection_patterns

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


def _build_policy_summary(policies):
    """One line per policy -- the same details shown in the Policies tab."""
    if not policies:
        return "The customer holds no policies."
    return "\n".join(
        f"- {p.policy_id}: {p.policy_type} / {p.sub_type}, status {p.status}, "
        f"coverage {p.start_date} to {p.end_date}, premium {p.premium}"
        for p in policies
    )


def _guarded_chat(db, customer_id, thread_id, user_message, send_fn):
    """
    The guardrails both chats share, in order:
      1. per-customer rate limit
      2. injection-style messages get a canned reply -- no AI call
      3. sensitive details are masked before the model (and its memory) ever see them
      4. per-thread message cap
      5. the model's reply is scrubbed (PII, other customers' IDs, "I approved
         your claim" statements, empty/oversized replies)
    send_fn takes the cleaned message and returns the model's raw reply.
    """
    check_rate_limit(
        f"chat:{customer_id}",
        constants.CHAT_RATE_LIMIT_MAX_MESSAGES,
        constants.CHAT_RATE_LIMIT_WINDOW_SECONDS,
        constants.CHAT_RATE_LIMITED,
    )

    if find_injection_patterns(user_message):
        logger.warning(f"GUARDRAIL injection-style chat message from customer {customer_id} -- canned reply")
        return constants.CHAT_INJECTION_REPLY

    clean_message, pii_found = mask_pii(user_message)
    if pii_found:
        logger.warning(f"GUARDRAIL PII masked in chat message from customer {customer_id}: {pii_found}")

    user_turns = sum(1 for turn in get_chat_history(thread_id) if turn["role"] == "user")
    if user_turns >= settings.max_chat_history_turns:
        logger.warning(f"GUARDRAIL chat thread {thread_id} reached its message cap ({user_turns})")
        raise RateLimitExceededError(constants.CHAT_LIMIT_REACHED)

    reply = guard_chat_reply(send_fn(clean_message), collect_allowed_ids(db, customer_id))
    if pii_found:
        reply = f"{constants.PII_NOTICE}\n\n{reply}"
    return reply


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

    reply = _guarded_chat(
        db, current_user.customer_id, thread_id, user_message,
        lambda message: send_claim_chat_message(thread_id, claim_context, claim.policy_id, message),
    )
    logger.info(f"Chat message handled for claim {claim_id} (customer {current_user.customer_id})")
    return reply


def send_policies_message(db, current_user, user_message):
    """
    Handle one message in the customer's shared Policies-tab chat. The
    policy list comes straight from the customer's own links, and the
    customer id from the login token, so the agent's tools can only ever
    search policies they hold and read their own claims.
    """
    policies = CustomerRepository(db).get_policies_for_customer(current_user.customer_id)
    owned_ids = [p.policy_id for p in policies]
    policy_summary = _build_policy_summary(policies)
    thread_id = f"{current_user.customer_id}:policies"

    reply = _guarded_chat(
        db, current_user.customer_id, thread_id, user_message,
        lambda message: send_policies_chat_message(
            thread_id, policy_summary, owned_ids, current_user.customer_id, message
        ),
    )
    logger.info(f"Policies chat message handled (customer {current_user.customer_id})")
    return reply


def get_claim_history(db, current_user, claim_id):
    """Earlier chat messages for one of the customer's own claims (same ownership check as sending)."""
    get_claim_detail(db, current_user, claim_id)
    return get_chat_history(f"{current_user.customer_id}:{claim_id}")


def get_policies_history(current_user):
    """Earlier messages in the customer's Policies-tab chat."""
    return get_chat_history(f"{current_user.customer_id}:policies")
