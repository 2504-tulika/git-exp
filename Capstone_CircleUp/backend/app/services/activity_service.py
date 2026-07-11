"""
Activity service — business logic for activity CRUD and discovery.

Database operations delegated to repository layer.
All ownership checks, status validations, and SRS rules live here.
Routers call these functions and never touch the database directly.
"""

import logging
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.constants import ActivityStatus
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

logger = logging.getLogger("app.services.activity")


def create_new_activity(db: Session, data: ActivityCreate, current_user: User) -> Activity:
    """
    Create a new activity.

    Creator is set from the JWT token — never from the request body.
    """
    logger.info(
        "Creating activity | user_id=%s | title=%r | category=%s | date=%s",
        current_user.id, data.title, data.category, data.activity_date
    )

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

    created = create_activity(db, new_activity)
    logger.info(
        "Activity created | id=%s | title=%r | creator_id=%s",
        created.id, created.title, created.creator_id
    )
    return created


def get_activity(db: Session, activity_id: int) -> Activity:
    """
    Fetch an activity by id.

    Raises 404 if not found.
    Lazily checks if activity should be marked as Completed.
    """
    activity = get_activity_by_id(db, activity_id)

    if not activity:
        logger.warning("Activity not found | activity_id=%s", activity_id)
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
    search: str | None = None,
    sort: str = "date_asc",
    skip: int = 0,
    limit: int = 20,
) -> list[Activity]:
    """
    Browse activities with optional filters and sorting.
    """
    from datetime import date as date_type

    parsed_date = None
    if date:
        parsed_date = date_type.fromisoformat(date)

    logger.debug(
        "Listing activities | category=%s | location=%s | date=%s | sort=%s | skip=%s | limit=%s",
        category, location, date, sort, skip, limit
    )

    activities = get_all_activities(
        db,
        category=category,
        location=location,
        activity_date=parsed_date,
        search=search,
        sort=sort,
        skip=skip,
        limit=min(limit, 50),
    )

    logger.debug("Returned %s activities", len(activities))
    return activities


def update_existing_activity(
    db: Session, activity_id: int, data: ActivityUpdate, current_user: User
) -> Activity:
    """
    Update an activity. Only the creator can update their own activity.
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

    if 'max_participants' in update_data:
        new_max = update_data['max_participants']
        approved_count = count_approved_participants(db, activity_id)

        # Rule 1 — cannot reduce below approved count
        if new_max < approved_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot reduce max participants to {new_max} — "
                    f"{approved_count} participants are already approved."
                ),
            )

        # Rule 2 — if Full but new max creates open spots, revert to Open
        if activity.status == ActivityStatus.FULL.value and new_max > approved_count:
            update_data['status'] = ActivityStatus.OPEN.value
        
    logger.info(
        "Updating activity | id=%s | user_id=%s | fields=%s",
        activity_id, current_user.id, list(update_data.keys())
    )

    for field, value in update_data.items():
        setattr(activity, field, value)

    updated = update_activity(db, activity)
    logger.info("Activity updated | id=%s", updated.id)
    return updated


def cancel_existing_activity(
    db: Session, activity_id: int, current_user: User
) -> Activity:
    """
    Cancel an activity. Only the creator can cancel.
    """
    activity = get_activity(db, activity_id)

    _check_ownership(activity, current_user)

    if activity.status == ActivityStatus.CANCELLED.value:
        logger.warning(
            "Cancel failed — already cancelled | activity_id=%s | user_id=%s",
            activity_id, current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Activity is already cancelled.",
        )

    if activity.status == ActivityStatus.COMPLETED.value:
        logger.warning(
            "Cancel failed — activity completed | activity_id=%s | user_id=%s",
            activity_id, current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a completed activity.",
        )

    activity.status = ActivityStatus.CANCELLED.value
    result = update_activity(db, activity)
    logger.info(
        "Activity cancelled | id=%s | by user_id=%s",
        activity_id, current_user.id
    )
    return result


def get_my_created_activities(db: Session, current_user: User) -> list[Activity]:
    """Get all activities created by the current user."""
    logger.debug("Fetching created activities | user_id=%s", current_user.id)
    return get_activities_by_creator(db, current_user.id)


# ── Private Helpers ───────────────────────────────────────────────────────────

def _check_ownership(activity: Activity, current_user: User) -> None:
    if activity.creator_id != current_user.id:
        logger.warning(
            "Ownership check failed | activity_id=%s | owner_id=%s | requester_id=%s",
            activity.id, activity.creator_id, current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this activity.",
        )


def _check_editable(activity: Activity) -> None:
    if activity.status in (
        ActivityStatus.CANCELLED.value,
        ActivityStatus.COMPLETED.value,
    ):
        logger.warning(
            "Edit rejected — terminal status | activity_id=%s | status=%s",
            activity.id, activity.status
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit a {activity.status} activity.",
        )


def _check_and_complete(db: Session, activity: Activity) -> Activity:
    """
    Lazily transition activity to Completed if its date/time has passed.
    """
    if activity.status in (ActivityStatus.OPEN.value, ActivityStatus.FULL.value):
        activity_datetime = datetime.combine(
            activity.activity_date,
            activity.activity_time,
        )
        if activity_datetime < datetime.now():
            logger.info(
                "Auto-completing activity | id=%s | was_status=%s",
                activity.id, activity.status
            )
            activity.status = ActivityStatus.COMPLETED.value
            return update_activity(db, activity)
    return activity