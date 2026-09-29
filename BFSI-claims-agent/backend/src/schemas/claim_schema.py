from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.config import constants


class ClaimSubmitRequest(BaseModel):
    policy_id: str = Field(..., min_length=1, max_length=20)
    claim_type: str = Field(..., min_length=1, max_length=constants.MAX_CLAIM_TYPE_LENGTH)
    incident_description: str = Field(..., min_length=1, max_length=constants.MAX_INCIDENT_DESCRIPTION_LENGTH)
    incident_date: date
    claim_amount: Optional[float] = Field(default=None, gt=0, le=constants.MAX_CLAIM_AMOUNT)

    @field_validator("policy_id", "claim_type", "incident_description")
    @classmethod
    def strip_and_require_text(cls, value, info):
        """Trim the text and reject a value that is only spaces."""
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name.replace('_', ' ').capitalize()} cannot be blank")
        return stripped

    @field_validator("incident_date")
    @classmethod
    def incident_date_not_in_future(cls, value):
        if value > date.today():
            raise ValueError("Incident date cannot be in the future")
        return value


class ClaimResponse(BaseModel):
    """
    The full claim record, including the agent's advisory output.
    ai_recommendation/ai_rationale are what the agent suggested -- status
    is the actual, human-decided outcome (starts "Under Review" for any
    claim submitted through the app, and stays that way until a handler
    acts on it). Never conflate the two when displaying this.
    """
    claim_id: str
    policy_id: str
    customer_id: str
    claim_type: str
    incident_date: date
    incident_description: Optional[str]
    intimation_date: date
    claim_amount: Optional[str]
    status: str
    fraud_flag: bool
    ai_recommendation: Optional[str]
    ai_rationale: Optional[str]
    # Only set on the response to a new submission, when sensitive details were hidden.
    privacy_notice: Optional[str] = None

    class Config:
        from_attributes = True


class PolicyResponse(BaseModel):
    """One policy the logged-in customer holds, for the 'list my policies' endpoint."""
    policy_id: str
    policy_type: str
    sub_type: str
    status: str
    start_date: date
    end_date: date
    premium: str

    class Config:
        from_attributes = True


