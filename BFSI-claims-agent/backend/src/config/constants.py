"""
User-facing message strings, centralized here instead of hardcoded inline at each raise site.
"""

# Auth
CUSTOMER_NOT_FOUND = "No customer found with the given customer ID."
USERNAME_TAKEN = "This username is already taken."
CUSTOMER_ALREADY_REGISTERED = "An account already exists for this customer ID."
INVALID_CREDENTIALS = "Incorrect username or password."
TOKEN_EXPIRED = "Your session has expired. Please log in again."
INVALID_TOKEN = "Invalid authentication token."

# Claims
MAX_CLAIMS_PER_POLICY_PER_YEAR = 5
CLAIM_LIMIT_REACHED = (
    "You have already filed {limit} claims on policy {policy_id} for {year}, "
    "which is the maximum allowed per year. This claim was not submitted. "
    "Please contact the claims team if you need help."
)

# Input limits
MAX_CLAIM_TYPE_LENGTH = 50
MAX_INCIDENT_DESCRIPTION_LENGTH = 300
MAX_CLAIM_AMOUNT = 100_000_00
MAX_CHAT_MESSAGE_LENGTH = 1000

# Rate limits (per customer)
CHAT_RATE_LIMIT_MAX_MESSAGES = 8
CHAT_RATE_LIMIT_WINDOW_SECONDS = 60
CLAIM_RATE_LIMIT_MAX_SUBMISSIONS = 3
CLAIM_RATE_LIMIT_WINDOW_SECONDS = 300

# Chat output limits
MAX_REPLY_CHARS = 3000

CHAT_RATE_LIMITED = "You're sending messages too quickly. Please wait a moment and try again."
CLAIM_RATE_LIMITED = (
    "You've submitted several claims in a short time. "
    "Please wait a few minutes before submitting another."
)
CHAT_LIMIT_REACHED = (
    "This conversation has reached its message limit. "
    "Please contact the claims team if you still need help."
)
CHAT_INJECTION_REPLY = (
    "I can't help with that request. I can answer questions about your "
    "policies and claims though -- what would you like to know?"
)
CHAT_UNSAFE_REPLY_FALLBACK = (
    "I can't approve, deny or change a claim -- only the claims team can do that. "
    "I can explain the existing review or your policy details, though."
)
CHAT_EMPTY_REPLY_FALLBACK = "Sorry, I couldn't put together an answer to that. Please try rephrasing your question."
PII_NOTICE = (
    "For your security, we hid some sensitive details (such as ID, card or "
    "contact numbers) in what you wrote. You don't need to include them."
)
REDACTED_ID = "[another record]"

DECISION_NOTE_NOT_ACTIVE = "Automated check: this policy is not active, so the claim cannot be approved."
DECISION_NOTE_OUTSIDE_PERIOD = "Automated check: the incident date falls outside this policy's coverage period."
DECISION_NOTE_FRAUD_SIGNALS = (
    "Automated check: risk signals were found on this claim, so it needs a manual check before approval."
)
DECISION_NOTE_INJECTION = (
    "Automated check: this claim contained instruction-like wording, so it needs a manual check before approval."
)
DECISION_NOTE_INCOMPLETE_CHECKS = (
    "Automated check: the full set of review checks was not completed, "
    "so this claim needs a manual check before approval."
)
