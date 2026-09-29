import re

from src.utils.logger import get_logger

logger = get_logger(__name__)

REQUIRED_FIELDS = ["policy_id", "customer_id", "claim_type", "incident_date"]

_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in [
        r"ignore (all |any )?(the )?(previous|prior|above|earlier|your) (instructions|rules|prompts?)",
        r"disregard (all |any )?(the )?(previous|prior|above|earlier|your) (instructions|rules|prompts?)",
        r"forget (all |any )?(the )?(previous|prior|above|earlier|your) (instructions|rules|prompts?)",
        r"you are now in \w+ mode",
        r"new instructions?:",
        r"(reveal|show|print|repeat|tell me) (me )?(your|the) (system )?(prompt|instructions|rules)",
        r"system prompt",
        r"(developer|debug|admin|god) mode",
        r"jailbreak",
        r"pretend (to be|you are|you're)",
        r"act as (an? )?(admin|administrator|claims (handler|manager)|the claims team)",
        r"approve (this|the|my) claim (automatically|immediately|now)",
        r"(mark|set) (this|the|my) claim (as )?approved",
        r"override (the )?(recommendation|decision|rules)",
    ]
]


def find_injection_patterns(text):
    """
    Return the list of injection patterns that match `text` (empty if
    none). Used to scan claim fields (logged, never blocking on its own)
    and chat messages (a match gets a polite canned reply instead of an
    AI call).
    """
    if not text:
        return []
    return [pattern.pattern for pattern in _INJECTION_PATTERNS if pattern.search(text)]


def pre_agent_check(claim):
    """
    Run deterministic checks on an incoming claim dict, before it reaches
    the agent at all.

    Returns {"missing_field_issues": [...], "should_block": bool,
    "injection_flags": [...]}. should_block is True only when a required
    field is missing -- injection_flags is informational, checked by the
    caller for logging, never for blocking.
    """
    missing_field_issues = []
    for field in REQUIRED_FIELDS:
        if not claim.get(field):
            missing_field_issues.append(f"Missing required field: {field}")

    injection_flags = []
    for field in ("incident_description", "claim_type"):
        for flagged in find_injection_patterns(claim.get(field) or ""):
            if flagged not in injection_flags:
                injection_flags.append(flagged)

    should_block = len(missing_field_issues) > 0

    result = {
        "missing_field_issues": missing_field_issues,
        "should_block": should_block,
        "injection_flags": injection_flags,
    }
    return result
