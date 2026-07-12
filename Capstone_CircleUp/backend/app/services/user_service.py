"""
User service — business logic for profile view and update.

Database operations delegated to repository layer.
Auth service handles credentials; this service handles profile data.
"""

import logging

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

logger = logging.getLogger("app.services.user")


def get_profile(user: User) -> User:
    """
    Return the current user's profile.
    No DB call needed — user is already loaded by get_current_user dependency.
    """
    logger.debug("Profile fetched | user_id=%s", user.id)
    return user


def update_profile(db: Session, user: User, data: UserUpdate) -> User:
    """
    Update allowed profile fields for the current user.

    Only fields explicitly provided in the request are updated.
    Email and password are not updatable here.
    """
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        logger.warning("Profile update failed — no fields provided | user_id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    logger.info(
        "Profile update | user_id=%s | fields=%s",
        user.id, list(update_data.keys())
    )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    logger.info("Profile updated successfully | user_id=%s", user.id)
    return user


def get_user_activities(db: Session, current_user: User) -> dict:
    """
    Get all activities related to the current user (created, joined, pending, rejected)
    along with dashboard statistics counts.
    """
    logger.debug("Fetching user activities | user_id=%s", current_user.id)

    created_raw = db.query(Activity).filter(Activity.creator_id == current_user.id).all()
    created = [_check_and_complete(db, a) for a in created_raw]

    requests = db.query(ParticipationRequest).filter(
        ParticipationRequest.user_id == current_user.id
    ).all()

    joined   = []
    pending  = []
    rejected = []

    for r in requests:
        act = _check_and_complete(db, r.activity)
        if r.status == RequestStatus.APPROVED.value:
            joined.append(act)
        elif r.status == RequestStatus.PENDING.value:
            pending.append(act)
        elif r.status == RequestStatus.REJECTED.value:
            rejected.append(act)

    completed_created = sum(1 for a in created if a.status == ActivityStatus.COMPLETED.value)
    completed_joined  = sum(1 for a in joined  if a.status == ActivityStatus.COMPLETED.value)
    completed_count   = completed_created + completed_joined

    stats = {
        "created":   len(created),
        "joined":    len(joined),
        "pending":   len(pending),
        "completed": completed_count,
    }

    logger.info(
        "Dashboard data ready | user_id=%s | stats=%s",
        current_user.id, stats
    )

    return {
        "created":  created,
        "joined":   joined,
        "pending":  pending,
        "rejected": rejected,
        "stats":    stats,
    }