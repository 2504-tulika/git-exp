from pydantic import BaseModel, Field, field_validator


class SignupRequest(BaseModel):
    """
    customer_id must be an existing customer already on file.
    """
    customer_id: str = Field(..., min_length=1)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_must_be_reasonably_strong(cls, value):
        if value.isalpha() or value.isdigit():
            raise ValueError("Password must contain a mix of letters and numbers, not just one or the other")
        return value


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """
    What signup/login hand back to describe the account itself --
    deliberately excludes password_hash, so it's always safe to return
    this directly in an API response.
    """
    id: int
    username: str
    customer_id: str

    class Config:
        from_attributes = True


