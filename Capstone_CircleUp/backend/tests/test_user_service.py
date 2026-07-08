import pytest
from datetime import date, time, timedelta
from fastapi import HTTPException
from app.services.user_service import get_profile, update_profile, get_user_activities
from app.schemas.user import UserUpdate
from app.models.activity import Activity
from app.models.participation_request import ParticipationRequest
from app.constants import ActivityStatus, RequestStatus

def test_get_profile(mock_user_1):
    """Verify get_profile returns the given user model object."""
    profile = get_profile(mock_user_1)
    assert profile.email == "alice@example.com"
    assert profile.name == "Alice Johnson"


def test_update_profile_success(db, mock_user_1):
    """Verify updating profile fields edits the user model attributes correctly."""
    update_data = UserUpdate(
        name="Alice J. Johnson",
        city="Los Angeles",
        phone="9876543210"
    )
    updated = update_profile(db, mock_user_1, update_data)
    assert updated.name == "Alice J. Johnson"
    assert updated.city == "Los Angeles"
    assert updated.phone == "9876543210"


def test_update_profile_no_fields_error(db, mock_user_1):
    """Verify updating profile with no fields raises a 400 Bad Request."""
    empty_update = UserUpdate()
    with pytest.raises(HTTPException) as exc:
        update_profile(db, mock_user_1, empty_update)
    assert exc.value.status_code == 400
    assert "No fields provided to update." in exc.value.detail


def test_get_user_activities_structure(db, mock_user_1, mock_user_2, mock_activity):
    """
    Verify get_user_activities compiles correct lists of created/joined activities
    and calculates accurate dashboard counts.
    - mock_activity is created by mock_user_1.
    - mock_user_2 requests to join mock_activity.
    """
    # Create request by mock_user_2
    req = ParticipationRequest(
        activity_id=mock_activity.id,
        user_id=mock_user_2.id,
        status=RequestStatus.PENDING.value
    )
    db.add(req)
    db.commit()

    # Get activities for Creator (mock_user_1)
    res_creator = get_user_activities(db, mock_user_1)
    assert len(res_creator["created"]) == 1
    assert res_creator["created"][0].id == mock_activity.id
    assert res_creator["stats"]["created"] == 1
    assert res_creator["stats"]["joined"] == 0

    # Get activities for Applicant (mock_user_2)
    res_applicant = get_user_activities(db, mock_user_2)
    assert len(res_applicant["pending"]) == 1
    assert res_applicant["pending"][0].id == mock_activity.id
    assert res_applicant["stats"]["pending"] == 1
    assert res_applicant["stats"]["joined"] == 0

    # Now approve the request and mark activity as completed to check stats
    req.status = RequestStatus.APPROVED.value
    mock_activity.status = ActivityStatus.COMPLETED.value
    db.commit()

    res_applicant_approved = get_user_activities(db, mock_user_2)
    assert len(res_applicant_approved["joined"]) == 1
    assert res_applicant_approved["stats"]["joined"] == 1
    assert res_applicant_approved["stats"]["completed"] == 1  # Completed count = completed_created (1 for creator) + completed_joined (1 for applicant)