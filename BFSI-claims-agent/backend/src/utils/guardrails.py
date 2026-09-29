"""
Guardrails that run AFTER the model (or around it), in plain Python.

  - enforce_decision_rules: re-checks the agent's recommendation against
    facts the code can verify itself (policy status/dates, fraud signals,
    which tools actually ran). The prompt asks the model to follow these
    rules; this makes sure they hold even if it doesn't.
  - guard_text / guard_chat_reply: scrub what the customer will read --
    PII, other customers' record IDs, "I approved your claim" style
    statements, empty or oversized replies.
  - check_rate_limit: per-customer sliding-window limits (in memory).

Every trigger is logged with a "GUARDRAIL" tag so it is easy to search for.
"""

import re
import threading
import time
from collections import defaultdict, deque

from src.config import constants
from src.exceptions.exceptions import RateLimitExceededError
from src.repositories.claims_repository import ClaimsRepository
from src.repositories.customer_repository import CustomerRepository
from src.utils.logger import get_logger
from src.utils.pii import mask_pii

logger = get_logger(__name__)

VALID_RECOMMENDATIONS = ("approve", "deny", "needs_more_info")
REQUIRED_TOOLS = {"check_coverage", "get_claims", "check_fraud_risk"}

# Record IDs that exist in this system: CUST-001, CLM-0001 / CLM-1A2B3C4D, MSI-MOT-1001.
_RECORD_ID = re.compile(r"\b(?:CUST-\d{3,}|CLM-[A-Z0-9]{4,8}|MSI-[A-Z]{3}-\d{4})\b")

# The assistant claiming to have made a decision or changed a claim.
_UNSAFE_REPLY_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in [
        r"\b(?:i|we)(?:'ve| have|'ll| will)?\s+(?:just\s+|now\s+)?(?:approved|denied|rejected|declined|overridden|reversed|reopened|cancell?ed)\b",
        r"\b(?:i|we)(?:'ll| will)\s+(?:go ahead and\s+)?(?:approve|deny|reject|override|reverse|reopen|cancel)\b",
        r"\b(?:i|we)(?:'ve| have|'ll| will)?\s+(?:just\s+|now\s+)?(?:changed|updated|modified|revised)\s+(?:your|the|this)\s+(?:claim|recommendation|status|decision)",
    ]
]


def enforce_decision_rules(recommendation, rationale, policy, incident_date,
                           claim_signals, tools_called, injection_flagged):
    """
    Re-check the agent's recommendation. Returns (recommendation, rationale).

    Coverage facts win over everything else (same order as the agent's own
    prompt): a policy that isn't Active, or an incident outside the coverage
    window, is a deny. An approve is then downgraded to needs_more_info if
    the claim has risk signals, its text looked like an injection attempt,
    or the agent skipped one of the three required checks. A note is added
    to the rationale only when something was actually changed.
    """
    original = recommendation
    if recommendation not in VALID_RECOMMENDATIONS:
        recommendation = "needs_more_info"

    note = None
    if policy.status != "Active":
        recommendation, note = "deny", constants.DECISION_NOTE_NOT_ACTIVE
    elif not (policy.start_date <= incident_date <= policy.end_date):
        recommendation, note = "deny", constants.DECISION_NOTE_OUTSIDE_PERIOD
    elif recommendation == "approve":
        if claim_signals:
            recommendation, note = "needs_more_info", constants.DECISION_NOTE_FRAUD_SIGNALS
        elif injection_flagged:
            recommendation, note = "needs_more_info", constants.DECISION_NOTE_INJECTION
        elif not REQUIRED_TOOLS.issubset(set(tools_called)):
            recommendation, note = "needs_more_info", constants.DECISION_NOTE_INCOMPLETE_CHECKS

    if recommendation != original:
        logger.warning(f"GUARDRAIL decision override: {original!r} -> {recommendation!r} ({note})")
        rationale = f"{rationale}\n\n{note}" if note else rationale
    return recommendation, rationale



def collect_allowed_ids(db, customer_id):
    """Every record ID this customer is allowed to see: themselves, their policies, their claims."""
    allowed = {customer_id}
    allowed.update(p.policy_id for p in CustomerRepository(db).get_policies_for_customer(customer_id))
    allowed.update(c.claim_id for c in ClaimsRepository(db).get_claims_for_customer(customer_id))
    return allowed


def _as_text(content):
    """A model reply is normally a string, but can be a list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block) for block in content
        )
    return "" if content is None else str(content)


def guard_text(text, allowed_ids):
    """
    Scrub text the customer will read: mask PII, and replace any record ID
    that isn't the customer's own (another customer's policy or claim).
    """
    text = _as_text(text)

    text, pii_found = mask_pii(text)
    if pii_found:
        logger.warning(f"GUARDRAIL output PII masked: {pii_found}")

    def _redact(match):
        if match.group() in allowed_ids:
            return match.group()
        logger.warning("GUARDRAIL output contained a record ID that is not the customer's own -- redacted")
        return constants.REDACTED_ID

    return _RECORD_ID.sub(_redact, text)


def guard_chat_reply(reply, allowed_ids):
    """guard_text plus the chat-only checks: no decisions, not empty, not oversized."""
    reply = guard_text(reply, allowed_ids).strip()

    if not reply:
        logger.warning("GUARDRAIL chat reply was empty -- fallback used")
        return constants.CHAT_EMPTY_REPLY_FALLBACK

    if any(pattern.search(reply) for pattern in _UNSAFE_REPLY_PATTERNS):
        logger.warning("GUARDRAIL chat reply claimed to make or change a decision -- replaced")
        return constants.CHAT_UNSAFE_REPLY_FALLBACK

    if len(reply) > constants.MAX_REPLY_CHARS:
        logger.warning(f"GUARDRAIL chat reply was {len(reply)} chars -- truncated")
        reply = reply[: constants.MAX_REPLY_CHARS].rstrip() + "..."
    return reply



class SlidingWindowRateLimiter:
    """Allow at most max_events per key in any window_seconds. In memory only."""

    def __init__(self):
        self._events = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key, max_events, window_seconds):
        now = time.monotonic()
        with self._lock:
            events = self._events[key]
            while events and now - events[0] > window_seconds:
                events.popleft()
            if len(events) >= max_events:
                return False
            events.append(now)
            return True


_rate_limiter = SlidingWindowRateLimiter()


def check_rate_limit(key, max_events, window_seconds, message):
    """Raise RateLimitExceededError(message) if `key` has hit its limit."""
    if not _rate_limiter.allow(key, max_events, window_seconds):
        logger.warning(f"GUARDRAIL rate limit hit: {key}")
        raise RateLimitExceededError(message)
