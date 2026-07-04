"""
Participation router — endpoints for requesting, approving,
and rejecting participation in activities.
Routes are thin — all business logic lives in participation_service.py.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.participation_request import (
    ParticipationRequestResponse,
    ParticipationRequestUpdate,
)
from app.services.participation_service import (
    request_to_join,
    get_contact_info,
    get_user_request,
    list_requests,
    approve_or_reject,
)

router = APIRouter(
    prefix="/activities/{activity_id}/requests",
    tags=["Participation"],
)


@router.post(
    "",
    response_model=ParticipationRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request to join an activity",
)
def join_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a participation request for an activity.

    Cannot request own activity, duplicate requests, or
    join Full/Cancelled/Completed activities.
    """
    return request_to_join(db, activity_id, current_user)

@router.get(
    "/me",
    response_model=ParticipationRequestResponse,
    summary="Get logged-in user's request status for this activity",
)
def get_my_request(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the current user's participation request for the activity.
    Returns 404 if no request exists.
    """
    return get_user_request(db, activity_id, current_user)

@router.get(
    "",
    response_model=list[ParticipationRequestResponse],
    summary="List participation requests (creator only)",
)

def get_requests(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all participation requests for an activity.
    Only the activity creator can access this endpoint.
    """
    return list_requests(db, activity_id, current_user)


@router.put(
    "/{request_id}",
    response_model=ParticipationRequestResponse,
    summary="Approve or reject a participation request",
)
def update_status(
    activity_id: int,
    request_id: int,
    data: ParticipationRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Approve or reject a participation request.

    Only the activity creator can approve or reject.
    Approval is concurrency-safe — won't exceed max_participants.
    Auto-transitions activity to Full when capacity is reached.
    """
    return approve_or_reject(db, activity_id, request_id, data.status, current_user)


@router.get(
    "/{request_id}/contact",
    summary="View contact info after approval",
)
def view_contact(
    activity_id: int,
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get contact info (phone) for both parties once a request is approved.

    Creator sees participant's phone, participant sees creator's phone.
    """
    return get_contact_info(db, activity_id, request_id, current_user)