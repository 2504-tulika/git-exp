from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class ClaimSubmitRequest(BaseModel):
    policy_id: str = Field(..., min_length=1)
    claim_type: str = Field(..., min_length=1)
    incident_description: str = Field(..., min_length=1)
    incident_date: date
    claim_amount: Optional[float] = Field(default=None, gt=0)


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


