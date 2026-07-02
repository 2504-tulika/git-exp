"""
Participation service — business logic for participation requests.

All SRS rules for requesting, approving, and rejecting live here.
Routers call these functions and never touch the database directly.
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity, ActivityStatus
from app.models.participation_request import ParticipationRequest, RequestStatus
from app.models.user import User


def create_request(
    db: Session, activity_id: int, current_user: User
) -> ParticipationRequest:
    """
    Submit a participation request for an activity.

    Rules enforced (SRS Section 6):
    - Cannot request own activity
    - Cannot request on Full, Cancelled, or Completed activities
    - Cannot submit a duplicate request (DB constraint + pre-check)
    """
    activity = _get_activity_or_404(db, activity_id)

    # Cannot request own activity
    if activity.creator_id == current_user.id:
        _bad_request("You cannot request to join your own activity.")

    # Only open activities accept new requests
    if activity.status == ActivityStatus.CANCELLED.value:
        _bad_request("Cannot request to join a cancelled activity.")

    if activity.status == ActivityStatus.COMPLETED.value:
        _bad_request("Cannot request to join a completed activity.")

    if activity.status == ActivityStatus.FULL.value:
        _bad_request("This activity is full and not accepting new requests.")

    # Check for duplicate request
    existing = db.query(ParticipationRequest).filter(
        ParticipationRequest.activity_id == activity_id,
        ParticipationRequest.user_id == current_user.id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already requested to join this activity.",
        )

    new_request = ParticipationRequest(
        activity_id=activity_id,
        user_id=current_user.id,
        status=RequestStatus.PENDING.value,
    )

    db.add(new_request)
    _commit(db)
    db.refresh(new_request)
    return new_request


def list_requests(
    db: Session, activity_id: int, current_user: User
) -> list[ParticipationRequest]:
    """
    List all participation requests for an activity.

    Only the activity creator can view requests (SRS Section 6).
    """
    activity = _get_activity_or_404(db, activity_id)
    _check_ownership(activity, current_user)

    return db.query(ParticipationRequest).filter(
        ParticipationRequest.activity_id == activity_id,
    ).all()

def get_user_request(
    db: Session, activity_id: int, current_user: User
) -> ParticipationRequest:
    """
    Get the participation request of the current user for a specific activity.
    Raises 404 if not found.
    """
    req = db.query(ParticipationRequest).filter(
        ParticipationRequest.activity_id == activity_id,
        ParticipationRequest.user_id == current_user.id,
    ).first()
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not requested to join this activity.",
        )
    return req

def update_request_status(
    db: Session,
    activity_id: int,
    request_id: int,
    new_status: str,
    current_user: User,
) -> ParticipationRequest:
    """
    Approve or reject a participation request.

    Only the activity creator can do this (SRS Section 6).

    Approval is concurrency-safe — uses SELECT FOR UPDATE to lock the
    activity row before checking capacity, preventing two simultaneous
    approvals from exceeding max_participants (SRS Section 7).
    """
    # Validate status value
    if new_status not in (RequestStatus.APPROVED.value, RequestStatus.REJECTED.value):
        _bad_request("Status must be 'approved' or 'rejected'.")

    # Lock activity row for concurrency safety on approval
    activity = db.execute(
        select(Activity)
        .where(Activity.id == activity_id)
        .with_for_update()
    ).scalar_one_or_none()

    if not activity:
        _not_found("Activity not found.")

    _check_ownership(activity, current_user)

    # Fetch the request
    participation_request = db.query(ParticipationRequest).filter(
        ParticipationRequest.id == request_id,
        ParticipationRequest.activity_id == activity_id,
    ).first()

    if not participation_request:
        _not_found("Participation request not found.")

    # Cannot change an already-decided request
    if participation_request.status != RequestStatus.PENDING.value:
        _bad_request(
            f"This request has already been {participation_request.status}."
        )

    # Capacity check before approving
    if new_status == RequestStatus.APPROVED.value:
        approved_count = db.query(ParticipationRequest).filter(
            ParticipationRequest.activity_id == activity_id,
            ParticipationRequest.status == RequestStatus.APPROVED.value,
        ).count()

        if approved_count >= activity.max_participants:
            _bad_request(
                "Cannot approve — activity has reached maximum capacity."
            )

        participation_request.status = RequestStatus.APPROVED.value

        # Auto-transition to Full if capacity is now reached
        if approved_count + 1 >= activity.max_participants:
            activity.status = ActivityStatus.FULL.value

    else:
        participation_request.status = RequestStatus.REJECTED.value

    _commit(db)
    db.refresh(participation_request)
    return participation_request


def get_approved_contact(
    db: Session,
    activity_id: int,
    request_id: int,
    current_user: User,
) -> dict:
    """
    Return contact info (phone) for both parties once a request is approved.

    SRS Section 8: contact info is only visible after approval.
    - Creator can see the approved participant's phone
    - Approved participant can see the creator's phone
    """
    activity = _get_activity_or_404(db, activity_id)

    participation_request = db.query(ParticipationRequest).filter(
        ParticipationRequest.id == request_id,
        ParticipationRequest.activity_id == activity_id,
    ).first()

    if not participation_request:
        _not_found("Participation request not found.")

    if participation_request.status != RequestStatus.APPROVED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contact info is only visible after a request is approved.",
        )

    # Only the creator or the approved participant can see contact info
    is_creator     = activity.creator_id == current_user.id
    is_participant = participation_request.user_id == current_user.id

    if not (is_creator or is_participant):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this contact info.",
        )

    # Fetch both users
    creator     = db.query(User).filter(User.id == activity.creator_id).first()
    participant = db.query(User).filter(
        User.id == participation_request.user_id
    ).first()

    return {
    "creator_phone":          creator.phone          if is_participant else None,
    "creator_social":         creator.social_handle  if is_participant else None,
    "participant_phone":      participant.phone       if is_creator    else None,
    "participant_social":     participant.social_handle if is_creator  else None,
    }


# Private Helpers

def _get_activity_or_404(db: Session, activity_id: int) -> Activity:
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        _not_found("Activity not found.")
    return activity


def _check_ownership(activity: Activity, current_user: User) -> None:
    if activity.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage this activity's requests.",
        )


def _commit(db: Session) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def _bad_request(detail: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=detail
    )


def _not_found(detail: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=detail
    )