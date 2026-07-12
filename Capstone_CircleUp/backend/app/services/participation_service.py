"""
Participation service — business logic for participation requests.

Database operations delegated to repository layer.
All SRS rules for requesting, approving, and rejecting live here.
Routers call these functions and never touch the database directly.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.participation_request import ParticipationRequest
from app.constants import ActivityStatus, RequestStatus
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

logger = logging.getLogger("app.services.participation")


def request_to_join(
    db: Session, activity_id: int, current_user: User
) -> ParticipationRequest:
    """
    Submit a participation request for an activity.
    """
    logger.info(
        "Join request | user_id=%s | activity_id=%s",
        current_user.id, activity_id
    )

    activity = get_activity_by_id(db, activity_id)

    if not activity:
        logger.warning("Join request failed — activity not found | activity_id=%s", activity_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    if activity.creator_id == current_user.id:
        logger.warning(
            "Join request failed — own activity | user_id=%s | activity_id=%s",
            current_user.id, activity_id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot request to join your own activity.",
        )

    if activity.status == ActivityStatus.CANCELLED.value:
        logger.warning(
            "Join request failed — activity cancelled | activity_id=%s", activity_id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot request to join a cancelled activity.",
        )

    if activity.status == ActivityStatus.COMPLETED.value:
        logger.warning(
            "Join request failed — activity completed | activity_id=%s", activity_id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot request to join a completed activity.",
        )

    if activity.status == ActivityStatus.FULL.value:
        logger.warning(
            "Join request failed — activity full | activity_id=%s", activity_id
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This activity is full and not accepting new requests.",
        )

    existing = get_by_activity_and_user(db, activity_id, current_user.id)
    if existing:
        logger.warning(
            "Join request failed — duplicate | user_id=%s | activity_id=%s",
            current_user.id, activity_id
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already requested to join this activity.",
        )

    new_request = ParticipationRequest(
        activity_id=activity_id,
        user_id=current_user.id,
        status=RequestStatus.PENDING.value,
    )

    created = create_request(db, new_request)
    logger.info(
        "Join request created | request_id=%s | user_id=%s | activity_id=%s",
        created.id, current_user.id, activity_id
    )
    return created


def get_user_request(
    db: Session, activity_id: int, current_user: User
) -> ParticipationRequest:
    """
    Get the current user's participation request for a specific activity.
    Raises 404 if no request exists.
    """
    req = get_by_activity_and_user(db, activity_id, current_user.id)
    if not req:
        logger.debug(
            "No request found | user_id=%s | activity_id=%s",
            current_user.id, activity_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No request found.",
        )
    return req


def list_requests(
    db: Session, activity_id: int, current_user: User
) -> list[ParticipationRequest]:
    """
    List all participation requests for an activity (creator only).
    """
    activity = get_activity_by_id(db, activity_id)

    if not activity:
        logger.warning("List requests failed — activity not found | activity_id=%s", activity_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    _check_ownership(activity, current_user)

    requests = get_requests_by_activity(db, activity_id)
    logger.debug(
        "Listed %s requests | activity_id=%s | requested_by user_id=%s",
        len(requests), activity_id, current_user.id
    )
    return requests


def approve_or_reject(
    db: Session,
    activity_id: int,
    request_id: int,
    new_status: str,
    current_user: User,
) -> ParticipationRequest:
    """
    Approve or reject a participation request (creator only).
    Concurrency-safe via SELECT FOR UPDATE.
    """
    logger.info(
        "Request status update | request_id=%s | new_status=%s | by user_id=%s",
        request_id, new_status, current_user.id
    )

    if new_status not in (RequestStatus.APPROVED.value, RequestStatus.REJECTED.value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'approved' or 'rejected'.",
        )

    activity = db.execute(
        select(Activity)
        .where(Activity.id == activity_id)
        .with_for_update()
    ).scalar_one_or_none()

    if not activity:
        logger.warning("Approve/reject failed — activity not found | activity_id=%s", activity_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found.",
        )

    _check_ownership(activity, current_user)

    participation_request = get_request_by_id(db, request_id)

    if not participation_request or participation_request.activity_id != activity_id:
        logger.warning(
            "Approve/reject failed — request not found | request_id=%s | activity_id=%s",
            request_id, activity_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation request not found.",
        )

    if participation_request.status != RequestStatus.PENDING.value:
        logger.warning(
            "Approve/reject failed — not pending | request_id=%s | current_status=%s",
            request_id, participation_request.status
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This request has already been {participation_request.status}.",
        )

    if new_status == RequestStatus.APPROVED.value:
        approved_count = count_approved_participants(db, activity_id)

        if approved_count >= activity.max_participants:
            logger.warning(
                "Approval rejected — activity at capacity | activity_id=%s | max=%s | approved=%s",
                activity_id, activity.max_participants, approved_count
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot approve — activity has reached maximum capacity.",
            )

        participation_request.status = RequestStatus.APPROVED.value

        if approved_count + 1 >= activity.max_participants:
            activity.status = ActivityStatus.FULL.value
            db.flush()
            logger.info(
                "Activity marked FULL after approval | activity_id=%s", activity_id
            )

    else:
        participation_request.status = RequestStatus.REJECTED.value

    result = update_request(db, participation_request)
    logger.info(
        "Request updated | request_id=%s | new_status=%s | activity_id=%s",
        result.id, result.status, activity_id
    )
    return result


def cancel_request(
    db: Session,
    activity_id: int,
    request_id: int,
    current_user: User,
) -> ParticipationRequest:
    """
    Cancel a pending participation request (requester only).
    """
    req = get_request_by_id(db, request_id)

    if not req or req.activity_id != activity_id:
        logger.warning(
            "Cancel request failed — not found | request_id=%s | activity_id=%s",
            request_id, activity_id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation request not found.",
        )

    if req.user_id != current_user.id:
        logger.warning(
            "Cancel request failed — not owner | request_id=%s | user_id=%s | owner_id=%s",
            request_id, current_user.id, req.user_id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own requests.",
        )

    if req.status != RequestStatus.PENDING.value:
        logger.warning(
            "Cancel request failed — not pending | request_id=%s | status=%s",
            request_id, req.status
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel a request that is already {req.status}.",
        )

    db.delete(req)
    db.commit()
    logger.info(
        "Request cancelled | request_id=%s | user_id=%s | activity_id=%s",
        request_id, current_user.id, activity_id
    )
    return req


def get_contact_info(
    db: Session,
    activity_id: int,
    request_id: int,
    current_user: User,
) -> dict:
    """
    Return contact info for both parties once a request is approved.
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
        logger.warning(
            "Contact info denied — request not approved | request_id=%s | status=%s",
            request_id, participation_request.status
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contact info is only visible after a request is approved.",
        )

    is_creator     = activity.creator_id == current_user.id
    is_participant = participation_request.user_id == current_user.id

    if not (is_creator or is_participant):
        logger.warning(
            "Contact info denied — unauthorized access | request_id=%s | user_id=%s",
            request_id, current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this contact info.",
        )

    creator     = db.query(User).filter(User.id == activity.creator_id).first()
    participant = db.query(User).filter(
        User.id == participation_request.user_id
    ).first()

    logger.info(
        "Contact info accessed | request_id=%s | by user_id=%s | role=%s",
        request_id, current_user.id, "creator" if is_creator else "participant"
    )

    return {
        "creator_phone":      creator.phone          if is_participant else None,
        "creator_social":     creator.social_handle  if is_participant else None,
        "participant_phone":  participant.phone       if is_creator    else None,
        "participant_social": participant.social_handle if is_creator  else None,
    }


# ── Private Helpers ───────────────────────────────────────────────────────────

def _check_ownership(activity: Activity, current_user: User) -> None:
    if activity.creator_id != current_user.id:
        logger.warning(
            "Ownership check failed | activity_id=%s | owner_id=%s | requester_id=%s",
            activity.id, activity.creator_id, current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage this activity's requests.",
        )