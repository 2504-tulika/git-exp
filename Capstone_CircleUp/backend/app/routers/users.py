"""
Users router — profile view and update endpoints.

Both routes are protected — require a valid JWT token.
The current user is injected via get_current_user dependency.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import get_profile, update_profile

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the profile of the currently logged-in user.
    """
    return get_profile(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
def update_my_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update profile fields for the currently logged-in user.

    Only fields included in the request body are updated.
    Email and password cannot be changed here.
    """
    return update_profile(db, current_user, data)