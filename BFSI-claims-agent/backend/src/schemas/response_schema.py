from pydantic import BaseModel


class MessageResponse(BaseModel):
    """A plain confirmation message, for any endpoint whose only real output is 'done'."""
    detail: str


class HealthResponse(BaseModel):
    """Used by health_router.py."""
    status: str


