"""
Pydantic schemas for user-related request and response shapes.

Schemas are strictly separated from models — models define how data is
stored, schemas define what comes in and goes out of the API. This means
we never accidentally expose password_hash in a response.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# Request Schemas 

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    social_handle: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty or whitespace.")
        if not re.match(r"^[a-zA-Z\s\-'.]+$", v):
            raise ValueError("Name can only contain letters, spaces, hyphens, apostrophes, and dots.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number.")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not re.match(r"^[1-9][0-9]{9}$", v):
            raise ValueError(
                "Enter a valid 10-digit mobile number ")
        return v

    @field_validator("social_handle")
    @classmethod
    def validate_social_handle(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        # must start with @, followed by letters/numbers/underscores/dots
        if not re.match(r"^@[\w.]{1,99}$", v):
            raise ValueError("Social handle must start with @ (e.g. @username).")
        return v

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Bio must be at least 10 characters if provided.")
        return v

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not re.match(r"^[a-zA-Z\s\-'.]+$", v):
            raise ValueError("City name can only contain letters, spaces, and hyphens.")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


# Response Schemas 

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    city: str | None
    bio: str | None
    social_handle: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse