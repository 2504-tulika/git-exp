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


class AgentToolError(ClaimsAgentError):
    """
    Raised when an MCP tool call or the LLM call itself fails (e.g. Groq
    or ChromaDB unreachable) -- lets claim_service.py degrade gracefully
    (mark the claim "needs manual review") instead of crashing with no
    audit trail.
    """
