"""
Pydantic schemas for activity-related request and response shapes.
"""

from datetime import date, datetime, time
from pydantic import BaseModel, Field, field_validator

from pydantic import BaseModel, Field, field_validator, model_validator

# Request Schemas 

class ActivityCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    category: str = Field(..., min_length=2, max_length=50)
    location: str = Field(..., min_length=2, max_length=200)
    activity_date: date
    activity_time: time
    max_participants: int = Field(..., gt=0)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty.")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Location cannot be empty.")
        return v

    @field_validator("activity_date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        if v < datetime.now().date():
            raise ValueError("Activity date must be in the future.")
        return v

    @field_validator("max_participants")
    @classmethod
    def validate_max_participants(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Maximum participants must be greater than zero.")
        return v
    
    @model_validator(mode="after")
    def validate_future_datetime(self) -> "ActivityCreate":
        """
        If the activity is scheduled for today, ensure the time
        is still in the future — not a past time on today's date.
        """
        from datetime import datetime as dt
        if self.activity_date and self.activity_time:
            activity_dt = dt.combine(self.activity_date, self.activity_time)
            if activity_dt <= dt.now():
                raise ValueError(
                    "Activity date and time must be in the future."
                )
        return self


class ActivityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    description: str | None = Field(default=None, max_length=1000)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    location: str | None = Field(default=None, min_length=2, max_length=200)
    activity_date: date | None = None
    activity_time: time | None = None
    max_participants: int | None = Field(default=None, gt=0)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty.")
        return v

    @field_validator("activity_date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        if v < datetime.now().date():
            raise ValueError("Activity date must be in the future.")
        return v

    @field_validator("max_participants")
    @classmethod
    def validate_max_participants(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v <= 0:
            raise ValueError("Maximum participants must be greater than zero.")
        return v


# Response Schemas 

class ActivityResponse(BaseModel):
    id: int
    creator_id: int
    creator_name: str | None = None
    title: str
    description: str | None
    category: str
    location: str
    activity_date: date
    activity_time: time
    max_participants: int | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}