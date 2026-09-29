"""
PII masking, shared by the claim flow, both chats, and the logger.

Deliberately dependency-free (regex + plain Python) and deliberately does
NOT import the logger -- the logger imports this module to filter its own
output, so importing it back would be circular.

What it covers (Indian formats): card numbers (Luhn-checked), phone
numbers, Aadhaar, PAN, IFSC, e-mail addresses, bank account numbers and
OTP/CVV/PIN/password values (the last two groups only when a keyword such
as "account" or "OTP" sits next to the number, so ordinary numbers like
claim amounts are left alone).

What it does NOT cover: names. Regex can't reliably find a name in free
text. The agent is never sent the customer's name, date of birth or
contact number in the first place.
"""

import logging
import re

_MASKS = [
    ("SECRET", re.compile(r"\b(?:otp|cvv|cvc|pin)\b\s*(?:is|=|:|-|number)?\s*\d{3,8}\b", re.IGNORECASE)),
    ("SECRET", re.compile(r"\b(?:password|passcode)\b\s*(?:is|=|:)\s*\S+", re.IGNORECASE)),
    (
        "BANK_ACCOUNT",
        re.compile(r"\b(?:a/c|acct|account)(?:\s*(?:no\.?|number|num|#))?\s*(?:is|:|-|=)?\s*\d{9,18}\b", re.IGNORECASE),
    ),
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("PHONE", re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}(?!\d)")),
    ("AADHAAR", re.compile(r"(?<!\d)[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}(?!\d)")),
    ("PAN", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")),
    ("IFSC", re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b")),
]

_CARD_CANDIDATE = re.compile(r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)")


def _passes_luhn(digits):
    """Standard card-number checksum -- filters out random long numbers."""
    total = 0
    for position, char in enumerate(reversed(digits)):
        value = int(char)
        if position % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def mask_pii(text):
    """
    Replace PII in `text` with placeholders like [AADHAAR] or [CARD].

    Returns (masked_text, found_types) where found_types is a sorted list
    of the kinds of PII that were found (empty if none). Safe to run twice
    on the same text -- the placeholders contain no digits to re-match.
    """
    if not isinstance(text, str) or not text:
        return text, []

    found = set()

    for label, pattern in _MASKS[:4]:
        text, count = pattern.subn(f"[{label}]", text)
        if count:
            found.add(label)

    def _replace_card(match):
        digits = re.sub(r"\D", "", match.group())
        if 13 <= len(digits) <= 19 and _passes_luhn(digits):
            found.add("CARD")
            return "[CARD]"
        return match.group()

    text = _CARD_CANDIDATE.sub(_replace_card, text)

    for label, pattern in _MASKS[4:]:
        text, count = pattern.subn(f"[{label}]", text)
        if count:
            found.add(label)

    return text, sorted(found)


class PiiLogFilter(logging.Filter):
    """Attach to a log handler so PII never reaches the console or app.log."""

    def filter(self, record):
        try:
            message = record.getMessage()
        except Exception:
            return True
        masked, found = mask_pii(message)
        if found:
            record.msg = masked
            record.args = None
        return True
