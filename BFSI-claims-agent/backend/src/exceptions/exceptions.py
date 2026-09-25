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
    AgentToolError: 502,
}


def _make_handler(status_code):
    async def handler(request, exc):
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})
    return handler


def register_exception_handlers(app):
    for exc_class, status_code in _STATUS_CODES.items():
        app.add_exception_handler(exc_class, _make_handler(status_code))


