"""
Users router — profile view, update, and dashboard endpoints.
All routes are protected — require a valid JWT token.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import get_profile, update_profile
from app.repositories import get_activities_by_creator, get_requests_by_user, get_requests_by_activity

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return get_profile(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user profile",
)
def update_my_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_profile(db, current_user, data)


@router.get(
    "/me/activities",
    summary="Get current user's created activities and participation requests",
)
def get_my_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns all activities created by the user, and all participation
    requests made by the user. Used by the Dashboard page.
    """
    created = get_activities_by_creator(db, current_user.id)
    all_requests = get_requests_by_user(db, current_user.id)

    def _fmt_activity(a, creator_name, pending_count=0):
        return {
            "id": a.id,
            "title": a.title,
            "category": a.category,
            "location": a.location,
            "activity_date": str(a.activity_date),
            "activity_time": str(a.activity_time),
            "max_participants": a.max_participants,
            "status": a.status,
            "creator_name": creator_name,
            "pending_requests_count": pending_count,
        }

    # For each created activity, count how many pending requests it has
    created_list = []
    total_pending_on_my_activities = 0
    for a in created:
        activity_requests = get_requests_by_activity(db, a.id)
        pending_count = sum(1 for r in activity_requests if r.status == "pending")
        total_pending_on_my_activities += pending_count
        created_list.append(_fmt_activity(a, current_user.name, pending_count))

    # Split requests the current user MADE (as participant) by status
    joined   = []
    pending  = []
    rejected = []

    for r in all_requests:
        if not r.activity:
            continue
        a = r.activity
        card = _fmt_activity(a, a.creator.name if a.creator else None)
        card["request_id"] = r.id
        card["request_status"] = r.status
        if r.status == "approved":
            joined.append(card)
        elif r.status == "pending":
            pending.append(card)
        elif r.status == "rejected":
            rejected.append(card)

    completed_count = sum(1 for a in created if a.status == "completed")

    return {
        "stats": {
            "created":   len(created_list),
            "joined":    len(joined),
            "pending":   total_pending_on_my_activities,  # requests waiting on MY activities
            "completed": completed_count,
        },
        "created":  created_list,
        "joined":   joined,
        "pending":  pending,
        "rejected": rejected,
    }
