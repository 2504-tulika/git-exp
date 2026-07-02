"""
Participation repository — all database operations for ParticipationRequest.

Handles request creation, status updates, and all query patterns
needed for participation management and contact visibility logic.
"""

from sqlalchemy.orm import Session

from app.models.participation_request import ParticipationRequest, RequestStatus


def get_by_id(db: Session, request_id: int) -> ParticipationRequest | None:
    return (
        db.query(ParticipationRequest)
        .filter(ParticipationRequest.id == request_id)
        .first()
    )


def get_by_activity_and_user(
    db: Session, activity_id: int, user_id: int
) -> ParticipationRequest | None:
    """
    Check if a user already has a request for this activity.
    Used to enforce the no-duplicate-request rule.
    """
    return (
        db.query(ParticipationRequest)
        .filter(
            ParticipationRequest.activity_id == activity_id,
            ParticipationRequest.user_id == user_id,
        )
        .first()
    )


def get_by_activity(
    db: Session, activity_id: int
) -> list[ParticipationRequest]:
    """
    Get all participation requests for an activity.
    Used by the creator to view and manage requests.
    """
    return (
        db.query(ParticipationRequest)
        .filter(ParticipationRequest.activity_id == activity_id)
        .order_by(ParticipationRequest.created_at.asc())
        .all()
    )


def get_by_user(
    db: Session, user_id: int
) -> list[ParticipationRequest]:
    """
    Get all participation requests made by a user.
    Used for the My Activities — Pending Requests view.
    """
    return (
        db.query(ParticipationRequest)
        .filter(ParticipationRequest.user_id == user_id)
        .order_by(ParticipationRequest.created_at.desc())
        .all()
    )


def get_approved_by_activity(
    db: Session, activity_id: int
) -> list[ParticipationRequest]:
    """
    Get only approved requests for an activity.
    Used for contact visibility — only approved participants
    can see each other's contact info.
    """
    return (
        db.query(ParticipationRequest)
        .filter(
            ParticipationRequest.activity_id == activity_id,
            ParticipationRequest.status == RequestStatus.APPROVED.value,
        )
        .all()
    )


def create(db: Session, request: ParticipationRequest) -> ParticipationRequest:
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def update(db: Session, request: ParticipationRequest) -> ParticipationRequest:
    db.commit()
    db.refresh(request)
    return request