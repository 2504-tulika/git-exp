"""
User service — business logic for profile view and update.

Database operations delegated to repository layer.
Auth service handles credentials; this service handles profile data.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories import update_user
from app.schemas.user import UserUpdate
from app.models.activity import Activity
from app.models.participation_request import ParticipationRequest
from app.constants import ActivityStatus, RequestStatus
from app.services.activity_service import _check_and_complete
from app.models.activity import Activity, ActivityStatus
from app.models.participation_request import ParticipationRequest, RequestStatus
from app.services.activity_service import _check_and_complete


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

def get_user_activities(db: Session, current_user: User) -> dict:

    """
    Get all activities related to the current user (created, joined, pending, rejected)
    along with dashboard statistics counts.
    """

    # Fetch created activities
    created_raw = db.query(Activity).filter(Activity.creator_id == current_user.id).all()
    created = [_check_and_complete(db, a) for a in created_raw]

    # Fetch participation requests by the user
    requests = db.query(ParticipationRequest).filter(
        ParticipationRequest.user_id == current_user.id
    ).all()
    joined = []
    pending = []
    rejected = []
    for r in requests:
        act = _check_and_complete(db, r.activity)
        if r.status == RequestStatus.APPROVED.value:
            joined.append(act)
        elif r.status == RequestStatus.PENDING.value:
            pending.append(act)
        elif r.status == RequestStatus.REJECTED.value:
            rejected.append(act)
    # Compute dashboard statistics
    created_count = len(created)
    joined_count = len(joined)
    pending_count = len(pending)

    completed_created = sum(1 for a in created if a.status == ActivityStatus.COMPLETED.value)
    completed_joined = sum(1 for a in joined if a.status == ActivityStatus.COMPLETED.value)
    completed_count = completed_created + completed_joined
    
    return {
        "created": created,
        "joined": joined,
        "pending": pending,
        "rejected": rejected,
        "stats": {
            "created": created_count,
            "joined": joined_count,
            "pending": pending_count,
            "completed": completed_count
        }
    }