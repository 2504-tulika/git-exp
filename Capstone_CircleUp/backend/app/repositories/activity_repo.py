"""
Activity repository — all database operations for the Activity model.

Includes filtering logic for activity discovery (browse, search, filters).
Services never write raw SQLAlchemy queries — they call these functions.
"""

from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.activity import Activity, ActivityStatus


def get_by_id(db: Session, activity_id: int) -> Activity | None:
    return db.query(Activity).filter(Activity.id == activity_id).first()


def create(db: Session, activity: Activity) -> Activity:
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def update(db: Session, activity: Activity) -> Activity:
    db.commit()
    db.refresh(activity)
    return activity


def get_all(
    db: Session,
    category: str | None = None,
    location: str | None = None,
    activity_date: date | None = None,
    search: str | None = None,
    sort: str = "date_asc",
    skip: int = 0,
    limit: int = 20,
) -> list[Activity]:
    """
    Browse activities with optional filters, search, and sorting.

    Excludes cancelled activities from results — users should
    only see open or full activities when browsing.
    """
    query = db.query(Activity).filter(
        Activity.status != ActivityStatus.CANCELLED.value
    )

    if category:
        query = query.filter(Activity.category == category)

    if location:
        query = query.filter(
            Activity.location.ilike(f"%{location}%")
        )

    if activity_date:
        query = query.filter(Activity.activity_date == activity_date)

    if search:
        query = query.filter(
            or_(
                Activity.title.ilike(f"%{search}%"),
                Activity.description.ilike(f"%{search}%"),
            )
        )

    if sort == "created_desc":
        query = query.order_by(Activity.created_at.desc())
    elif sort == "date_desc":
        query = query.order_by(Activity.activity_date.desc(), Activity.activity_time.desc())
    else:  # date_asc
        query = query.order_by(Activity.activity_date.asc(), Activity.activity_time.asc())

    return query.offset(skip).limit(limit).all()


def get_by_creator(db: Session, creator_id: int) -> list[Activity]:
    return (
        db.query(Activity)
        .filter(Activity.creator_id == creator_id)
        .order_by(Activity.created_at.desc())
        .all()
    )


def count_approved_participants(db: Session, activity_id: int) -> int:
    from app.models.participation_request import ParticipationRequest, RequestStatus
    return (
        db.query(ParticipationRequest)
        .filter(
            ParticipationRequest.activity_id == activity_id,
            ParticipationRequest.status == RequestStatus.APPROVED.value,
        )
        .count()
    )