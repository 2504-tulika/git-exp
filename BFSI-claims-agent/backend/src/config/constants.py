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

