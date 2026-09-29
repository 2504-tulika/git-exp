from fastapi.responses import JSONResponse


class ClaimsAgentError(Exception):
    """Base class every custom exception in this project inherits from."""


class CustomerNotFoundError(ClaimsAgentError):
    """Raised when a customer_id doesn't exist."""


class UsernameTakenError(ClaimsAgentError):
    """Raised on signup when the chosen username is already in use."""


class InvalidCredentialsError(ClaimsAgentError):
    """Raised on login when the username/password don't match."""


class PolicyNotFoundError(ClaimsAgentError):
    """Raised when a policy_id doesn't exist."""


class ClaimNotFoundError(ClaimsAgentError):
    """Raised when a claim_id doesn't exist."""


class UnauthorizedPolicyAccessError(ClaimsAgentError):
    """
    Raised when a customer_id is not actually a policyholder on the
    policy_id they're trying to act on -- the core authorization guard
    every claims/chat/tool code path relies on.
    """


class CustomerAlreadyRegisteredError(ClaimsAgentError):
    """
    Raised on signup when customer_id already has a login account.
    customer_id is unique on the User model -- this is the clean,
    checked-before-insert version of that constraint, not a raw
    IntegrityError from the database.
    """


class TokenExpiredError(ClaimsAgentError):
    """Raised when a JWT is well-formed and correctly signed, but its exp claim has passed."""


class InvalidTokenError(ClaimsAgentError):
    """
    Raised when a JWT is malformed, has a bad signature, or refers to a
    user that no longer exists -- anything about the token itself being
    wrong, as opposed to it simply having expired.
    """


class AgentToolError(ClaimsAgentError):
    """
    Raised when an MCP tool call or the LLM call itself fails (e.g. Groq
    or ChromaDB unreachable) -- lets claim_service.py degrade gracefully
    (mark the claim "needs manual review") instead of crashing with no
    audit trail.
    """

class ClaimLimitExceededError(ClaimsAgentError):
    """
    Raised when a customer has already filed the maximum number of claims
    allowed on one policy for the year (see MAX_CLAIMS_PER_POLICY_PER_YEAR
    in constants.py). The claim is rejected before the agent ever runs.
    """


class ChatNotAvailableError(ClaimsAgentError):
    """
    Raised when a customer tries to chat about a claim that has no AI
    recommendation yet (a seeded historical claim, or one still being
    processed) -- there is nothing for the chat to discuss.
    """


class RateLimitExceededError(ClaimsAgentError):
    """
    Raised when a customer sends chat messages or submits claims faster
    than the guardrail limits allow, or a chat thread has hit its message cap.
    """


_STATUS_CODES = {
    CustomerNotFoundError: 404,
    PolicyNotFoundError: 404,
    ClaimNotFoundError: 404,
    UsernameTakenError: 409,
    CustomerAlreadyRegisteredError: 409,
    InvalidCredentialsError: 401,
    TokenExpiredError: 401,
    InvalidTokenError: 401,
    UnauthorizedPolicyAccessError: 403,
    ClaimLimitExceededError: 422,
    ChatNotAvailableError: 409,
    AgentToolError: 502,
    RateLimitExceededError: 429,
}


def _make_handler(status_code):
    async def handler(request, exc):
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})
    return handler


def register_exception_handlers(app):
    for exc_class, status_code in _STATUS_CODES.items():
        app.add_exception_handler(exc_class, _make_handler(status_code))
