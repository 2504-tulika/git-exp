"""
Auth service — business logic for registration and login.

Database operations delegated to repository layer.
This service only handles credential verification,
password hashing, and token creation.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories import get_user_by_email, create_user
from app.schemas.user import UserRegister


def register_user(db: Session, data: UserRegister) -> User:
    """
    Register a new user.

    Raises 409 if email is already taken.
    Hashes the password before saving — plain password never hits the DB.
    """
    existing = get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        phone=data.phone,
        gender=data.gender,
        city=data.city,
        bio=data.bio,
        social_handle=data.social_handle,
    )

    return create_user(db, new_user)


def login_user(db: Session, email: str, password: str) -> dict:
    """
    Verify credentials and return a JWT token + user object.

    Raises 401 if email not found or password is wrong.
    Same error message for both cases — never reveal which one failed.
    """
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(subject=str(user.id))

    return {"access_token": access_token, "token_type": "bearer", "user": user}