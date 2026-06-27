"""
Activities router — CRUD endpoints for activities.

Routes are thin — they only handle HTTP concerns.
All business logic lives in activity_service.py.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityResponse, ActivityUpdate
from app.services.activity_service import (
    cancel_activity,
    create_activity,
    get_activity_by_id,
    update_activity,
)

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new activity",
)
def create(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new activity.

    The creator is automatically set from the JWT token.
    Activity starts with status Open.
    """
    return create_activity(db, data, current_user)


@router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="Get activity details",
)
def get_one(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get details of a specific activity by ID.

    Automatically transitions to Completed if date has passed.
    """
    return get_activity_by_id(db, activity_id)


@router.put(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="Update an activity",
)
def update(
    activity_id: int,
    data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an activity.

    Only the creator can update their own activity.
    Cannot update cancelled or completed activities.
    """
    return update_activity(db, activity_id, data, current_user)


@router.delete(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="Cancel an activity",
)
def cancel(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel an activity.

    Only the creator can cancel their own activity.
    Sets status to Cancelled — does not delete from database.
    """
    return cancel_activity(db, activity_id, current_user)