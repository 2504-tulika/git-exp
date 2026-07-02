"""
Activity service — business logic for activity CRUD and discovery.

Database operations delegated to repository layer.
All ownership checks, status validations, and SRS rules live here.
Routers call these functions and never touch the database directly.
"""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity, ActivityStatus
from app.models.user import User
from app.repositories import (
    get_activity_by_id,
    create_activity,
    update_activity,
    get_all_activities,
    get_activities_by_creator,
    count_approved_participants,
)
from app.schemas.activity import ActivityCreate, ActivityUpdate


def create_new_activity(db: Session, data: ActivityCreate, current_user: User) -> Activity:
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

    return create_activity(db, new_activity)


def get_activity(db: Session, activity_id: int) -> Activity:
    """
    Fetch an activity by id.

    Raises 404 if not found.
    Lazily checks if activity should be marked as Completed.
    """
    activity = get_activity_by_id(db, activity_id)

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    return _check_and_complete(db, activity)


def list_all_activities(
    db: Session,
    category: str | None = None,
    location: str | None = None,
    date: str | None = None,
    sort: str = "date_asc",
    skip: int = 0,
    limit: int = 20,
) -> list[Activity]:
    """
    Browse activities with optional filters and sorting.

    Shows Open, Full, and Cancelled activities.
    Completed activities are hidden from the discovery feed.
    """
    from datetime import date as date_type

    parsed_date = None
    if date:
        parsed_date = date_type.fromisoformat(date)

    activities = get_all_activities(
        db,
        category=category,
        location=location,
        activity_date=parsed_date,
        skip=skip,
        limit=min(limit, 50),
    )

    # Apply sort
    reverse = sort == "date_desc"
    activities.sort(
        key=lambda a: (a.activity_date, a.activity_time),
        reverse=reverse,
    )

    return activities


def update_existing_activity(
    db: Session, activity_id: int, data: ActivityUpdate, current_user: User
) -> Activity:
    """
    Update an activity.

    Only the creator can update their own activity.
    Cancelled or Completed activities cannot be edited.
    """
    activity = get_activity(db, activity_id)

    _check_ownership(activity, current_user)
    _check_editable(activity)

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )

    for field, value in update_data.items():
        setattr(activity, field, value)

    return update_activity(db, activity)


def cancel_existing_activity(
    db: Session, activity_id: int, current_user: User
) -> Activity:
    """
    Cancel an activity.

    Only the creator can cancel their own activity.
    Already cancelled or completed activities cannot be cancelled again.
    """
    activity = get_activity(db, activity_id)

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
    return update_activity(db, activity)


def get_my_created_activities(db: Session, current_user: User) -> list[Activity]:
    """
    Get all activities created by the current user.
    Used for the My Activities — Created tab.
    """
    return get_activities_by_creator(db, current_user.id)


# ── Private Helpers ───────────────────────────────────────────────────────────

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


def _check_editable(activity: Activity) -> None:
    """Raise 400 if the activity is in a terminal state."""
    if activity.status in (
        ActivityStatus.CANCELLED.value,
        ActivityStatus.COMPLETED.value,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit a {activity.status} activity.",
        )


def _check_and_complete(db: Session, activity: Activity) -> Activity:
    """
    Lazily transition activity to Completed if its date/time has passed.

    Runs on every read — no background scheduler needed.
    Only Open or Full activities transition to Completed.
    Cancelled stays Cancelled.
    """
    if activity.status in (ActivityStatus.OPEN.value, ActivityStatus.FULL.value):
        activity_datetime = datetime.combine(
            activity.activity_date,
            activity.activity_time,
        )
        if activity_datetime < datetime.now():
            activity.status = ActivityStatus.COMPLETED.value
            return update_activity(db, activity)
    return activity