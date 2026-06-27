"""
Activity service — business logic for activity CRUD operations.

All ownership checks, status validations, and SRS rules live here.
Routers call these functions and never touch the database directly.
"""

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity, ActivityStatus
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityUpdate


def create_activity(db: Session, data: ActivityCreate, current_user: User) -> Activity:
    """
    Create a new activity.

    Creator is set from the JWT token — never from the request body.
    This prevents users from creating activities on behalf of others.
    """
    new_activity = Activity(
        creator_id=current_user.id,
        title=data.title,
        description=data.description,
        category=data.category,
        location=data.location,
        activity_date=data.activity_date,
        activity_time=data.activity_time,
        max_participants=data.max_participants,
        status=ActivityStatus.OPEN.value,
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


def get_activity_by_id(db: Session, activity_id: int) -> Activity:
    """
    Fetch an activity by id.

    Raises 404 if not found.
    Also lazily checks if activity should be marked as Completed.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    # Lazy status transition — if date has passed, mark as Completed
    activity = _check_and_complete(db, activity)
    return activity


def update_activity(
    db: Session, activity_id: int, data: ActivityUpdate, current_user: User
) -> Activity:
    """
    Update an activity.

    Only the creator can update their own activity.
    Cancelled or Completed activities cannot be edited.
    """
    activity = get_activity_by_id(db, activity_id)

    _check_ownership(activity, current_user)

    if activity.status in [ActivityStatus.CANCELLED.value, ActivityStatus.COMPLETED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit a {activity.status} activity.",
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity


def cancel_activity(
    db: Session, activity_id: int, current_user: User
) -> Activity:
    """
    Cancel an activity.

    Only the creator can cancel their own activity.
    Already cancelled or completed activities cannot be cancelled again.
    """
    activity = get_activity_by_id(db, activity_id)

    _check_ownership(activity, current_user)

    if activity.status == ActivityStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity is already cancelled.",
        )

    if activity.status == ActivityStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed activity.",
        )

    activity.status = ActivityStatus.CANCELLED.value
    db.commit()
    db.refresh(activity)
    return activity


# Private Helpers 

def _check_ownership(activity: Activity, current_user: User) -> None:
    """
    Raise 403 if the current user is not the activity creator.

    Using 403 Forbidden (not 404) — the activity exists, the user
    just doesn't have permission to modify it.
    """
    if activity.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this activity.",
        )


def _check_and_complete(db: Session, activity: Activity) -> Activity:
    """
    Lazily transition activity to Completed if its date/time has passed.

    This runs on every read — no background scheduler needed.
    Only Open or Full activities transition to Completed.
    Cancelled stays Cancelled.
    """
    if activity.status in [ActivityStatus.OPEN.value, ActivityStatus.FULL.value]:
        activity_datetime = datetime.combine(
            activity.activity_date,
            activity.activity_time,
        )
        if activity_datetime < datetime.now():
            activity.status = ActivityStatus.COMPLETED.value
            db.commit()
            db.refresh(activity)
    return activity