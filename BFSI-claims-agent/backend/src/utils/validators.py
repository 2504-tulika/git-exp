"""
Deterministic, pre-LLM guardrail checks for an incoming claim.

Two separate concerns, kept deliberately separate:
  - missing_field_issues / should_block: hard checks that run BEFORE any
    Groq call is made. If a claim is missing something a tool genuinely
    needs, there's no reason to spend an LLM call finding that out. This
    is the actual, enforced guardrail.
  - injection_flags: pattern-matching over free-text fields, logged for
    audit visibility but NEVER used to block a claim by itself. A
    legitimate customer's claim can coincidentally contain phrasing that
    matches a pattern; the real defense against prompt injection is the
    agent's own system prompt instruction (see claims_agent.py) to treat
    claim content strictly as data, never as instructions. This is an
    observability signal, not a security boundary.
"""

import re

from src.utils.logger import get_logger

logger = get_logger(__name__)

REQUIRED_FIELDS = ["policy_id", "customer_id", "claim_type", "incident_date"]

_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in [
        r"ignore (all )?previous instructions",
        r"disregard (all )?(the )?(previous|above) instructions",
        r"you are now in \w+ mode",
        r"new instructions?:",
        r"system prompt",
        r"act as (an? )?admin",
        r"approve (this|the) claim automatically",
    ]
]


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
    incident_description = claim.get("incident_description") or ""
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(incident_description):
            injection_flags.append(pattern.pattern)

    should_block = len(missing_field_issues) > 0

    result = {
        "missing_field_issues": missing_field_issues,
        "should_block": should_block,
        "injection_flags": injection_flags,
    }
    return result
