"""
Activity service — business logic for activity CRUD operations.

All ownership checks, status validations, and SRS rules live here.
Routers call these functions and never touch the database directly.
"""

from datetime import datetime

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
    _commit(db)
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
        _not_found("Activity not found.")

    activity = _check_and_complete(db, activity)
    return activity


def list_activities(
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
    Completed activities are hidden — past activities aren't discoverable.
    Filters can be combined freely.

    Params:
        category  — exact match on activity category
        location  — case-insensitive partial match on location
        date      — filter to activities on this exact date (YYYY-MM-DD)
        sort      — 'date_asc' (soonest first, default) or 'date_desc'
        skip      — pagination offset
        limit     — page size (max 50)
    """
    # Never show completed activities in the discovery feed
    visible_statuses = [
        ActivityStatus.OPEN.value,
        ActivityStatus.FULL.value,
        ActivityStatus.CANCELLED.value,
    ]

    query = db.query(Activity).filter(Activity.status.in_(visible_statuses))

    # Apply filters
    if category:
        query = query.filter(Activity.category == category.lower())

    if location:
        # Case-insensitive partial match — "pune" matches "Pune" or "Kothrud, Pune"
        query = query.filter(Activity.location.ilike(f"%{location}%"))

    if date:
        from datetime import date as date_type
        parsed_date = date_type.fromisoformat(date)
        query = query.filter(Activity.activity_date == parsed_date)

    # Apply sort
    if sort == "date_desc":
        query = query.order_by(
            Activity.activity_date.desc(),
            Activity.activity_time.desc(),
        )
    else:
        # Default: soonest first
        query = query.order_by(
            Activity.activity_date.asc(),
            Activity.activity_time.asc(),
        )

    # Clamp limit to 50 to prevent abuse
    limit = min(limit, 50)

    return query.offset(skip).limit(limit).all()


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
    _check_editable(activity)

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        _bad_request("No fields provided to update.")

    for field, value in update_data.items():
        setattr(activity, field, value)

    _commit(db)
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
        _bad_request("Activity is already cancelled.")

    if activity.status == ActivityStatus.COMPLETED.value:
        _bad_request("Cannot cancel a completed activity.")

    activity.status = ActivityStatus.CANCELLED.value
    _commit(db)
    db.refresh(activity)
    return activity


# Private Helpers

def _commit(db: Session) -> None:
    """
    Commit the current session, rolling back on failure.

    Centralizes commit/rollback so every write path in this service handles DB errors the same way 
    """
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def _bad_request(detail: str) -> None:
    """Raise a centralized 400 Bad Request."""
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _not_found(detail: str) -> None:
    """Raise a centralized 404 Not Found."""
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


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
    """
    Raise 400 if the activity is in a terminal state (Cancelled/Completed)
    """
    if activity.status in (ActivityStatus.CANCELLED.value, ActivityStatus.COMPLETED.value):
        _bad_request(f"Cannot edit a {activity.status} activity.")


def _check_and_complete(db: Session, activity: Activity) -> Activity:
    """
    Lazily transition activity to Completed if its date/time has passed.

    This runs on every read — no background scheduler needed.
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
            _commit(db)
            db.refresh(activity)
    return activity