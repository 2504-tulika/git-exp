"""
Participation service — business logic for participation requests.

Database operations delegated to repository layer.
All SRS rules for requesting, approving, and rejecting live here.
Routers call these functions and never touch the database directly.
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity, ActivityStatus
from app.models.participation_request import ParticipationRequest, RequestStatus
from app.models.user import User
from app.repositories import (
    get_activity_by_id,
    get_by_activity_and_user,
    get_requests_by_activity,
    create_request,
    update_request,
    get_request_by_id,
    count_approved_participants,
)


def request_to_join(
    db: Session, activity_id: int, current_user: User
) -> ParticipationRequest:
    """
    Submit a participation request for an activity.

    Rules enforced (SRS):
    - Cannot request own activity
    - Cannot request on Full, Cancelled, or Completed activities
    - Cannot submit a duplicate request
    """
    activity = get_activity_by_id(db, activity_id)

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    if activity.creator_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot request to join your own activity.",
        )

    if activity.status == ActivityStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot request to join a cancelled activity.",
        )

    if activity.status == ActivityStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot request to join a completed activity.",
        )

    if activity.status == ActivityStatus.FULL.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This activity is full and not accepting new requests.",
        )

    existing = get_by_activity_and_user(db, activity_id, current_user.id)
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

    return create_request(db, new_request)


def get_user_request(
    db: Session, activity_id: int, current_user: User
) -> ParticipationRequest:
    """
    Get the current user's participation request for a specific activity.
    Raises 404 if no request exists (so frontend can distinguish no-request from error).
    """
    req = get_by_activity_and_user(db, activity_id, current_user.id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No request found.",
        )
    return req


def list_requests(
    db: Session, activity_id: int, current_user: User
) -> list[ParticipationRequest]:
    """
    List all participation requests for an activity.

    Only the activity creator can view requests (SRS).
    """
    activity = get_activity_by_id(db, activity_id)

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    _check_ownership(activity, current_user)

    requests = get_requests_by_activity(db, activity_id)
    return requests


def approve_or_reject(
    db: Session,
    activity_id: int,
    request_id: int,
    new_status: str,
    current_user: User,
) -> ParticipationRequest:
    """
    Approve or reject a participation request.

    Only the activity creator can do this (SRS).
    Approval is concurrency-safe — uses SELECT FOR UPDATE to lock the
    activity row before checking capacity, preventing two simultaneous
    approvals from exceeding max_participants.
    """
    if new_status not in (RequestStatus.APPROVED.value, RequestStatus.REJECTED.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'approved' or 'rejected'.",
        )

    # Lock activity row for concurrency safety
    activity = db.execute(
        select(Activity)
        .where(Activity.id == activity_id)
        .with_for_update()
    ).scalar_one_or_none()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    _check_ownership(activity, current_user)

    participation_request = get_request_by_id(db, request_id)

    if not participation_request or participation_request.activity_id != activity_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation request not found.",
        )

    if participation_request.status != RequestStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This request has already been {participation_request.status}.",
        )

    if new_status == RequestStatus.APPROVED.value:
        approved_count = count_approved_participants(db, activity_id)

        if approved_count >= activity.max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot approve — activity has reached maximum capacity.",
            )

        participation_request.status = RequestStatus.APPROVED.value

        # Auto-transition to Full if capacity is now reached
        if approved_count + 1 >= activity.max_participants:
            activity.status = ActivityStatus.FULL.value
            db.flush()

    else:
        participation_request.status = RequestStatus.REJECTED.value

    result = update_request(db, participation_request)
    return result


def get_contact_info(
    db: Session,
    activity_id: int,
    request_id: int,
    current_user: User,
) -> dict:
    """
    Return contact info for both parties once a request is approved.

    SRS: contact info only visible after approval.
    Creator sees participant's phone, participant sees creator's phone.
    """
    activity = get_activity_by_id(db, activity_id)

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    participation_request = get_request_by_id(db, request_id)

    if not participation_request or participation_request.activity_id != activity_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation request not found.",
        )

    if participation_request.status != RequestStatus.APPROVED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contact info is only visible after a request is approved.",
        )

    is_creator     = activity.creator_id == current_user.id
    is_participant = participation_request.user_id == current_user.id

    if not (is_creator or is_participant):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this contact info.",
        )

    creator     = db.query(User).filter(User.id == activity.creator_id).first()
    participant = db.query(User).filter(
        User.id == participation_request.user_id
    ).first()

    return {
        "creator_phone":       creator.phone          if is_participant else None,
        "creator_social":      creator.social_handle  if is_participant else None,
        "participant_phone":   participant.phone       if is_creator    else None,
        "participant_social":  participant.social_handle if is_creator  else None,
    }


# ── Private Helpers ───────────────────────────────────────────────────────────

def _check_ownership(activity: Activity, current_user: User) -> None:
    if activity.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage this activity's requests.",
        )