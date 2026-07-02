"""
Pydantic schemas for participation request shapes.

Strictly separated from the model — defines what comes in and out
of the API, not how data is stored.
"""

from datetime import datetime
from pydantic import BaseModel


# Request Schemas

class ParticipationRequestCreate(BaseModel):
    """No body needed — activity_id comes from the URL, user_id from JWT."""
    pass


class ParticipationRequestUpdate(BaseModel):
    """Approve or reject a request. Only the creator sends this."""
    status: str  # "approved" or "rejected"

# Response Schemas

class ParticipationRequestResponse(BaseModel):
    id: int
    activity_id: int
    user_id: int
    user_name: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParticipationRequestWithContact(BaseModel):
    """
    Extended response that includes the requester's contact info.
    Only returned to the activity creator once a request is approved.
    Phone is the only contact field per SRS Section 8.
    """
    id: int
    activity_id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    # Contact info — only populated when status is approved
    requester_name: str | None = None
    requester_phone: str | None = None

    model_config = {"from_attributes": True}