"""
User service — business logic for profile view and update.

Separating profile logic from auth logic keeps each service focused.
Auth service handles credentials; this service handles profile data.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserUpdate


def get_profile(user: User) -> User:
    """
    Return the current user's profile.
    No DB call needed — user is already loaded by get_current_user dependency.
    """
    return user


def update_profile(db: Session, user: User, data: UserUpdate) -> User:
    """
    Update allowed profile fields for the current user.

    Only fields explicitly provided in the request are updated.
    Email and password are not updatable here — separate flows for those.
    """
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user