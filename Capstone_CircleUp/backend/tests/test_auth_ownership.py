import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.constants import ActivityStatus, RequestStatus
from app.models.participation_request import ParticipationRequest
from app.services.activity_service import update_existing_activity, cancel_existing_activity
from app.services.participation_service import (
    request_to_join,
    list_requests,
    approve_or_reject,
    cancel_request,
    get_contact_info
)
from app.schemas.activity import ActivityUpdate

def test_creator_cannot_join_own_activity(db, mock_user_1, mock_activity):
    """
    Verify that a user cannot request to join their own activity.
    mock_activity is created by mock_user_1.
    """
    with pytest.raises(HTTPException) as exc:
        request_to_join(db, mock_activity.id, mock_user_1)
        
    assert exc.value.status_code == 400
    assert "You cannot request to join your own activity." in exc.value.detail


def test_only_creator_can_update_activity(db, mock_user_1, mock_user_2, mock_activity):
    """
    Verify that only the activity creator can update the activity details.
    - mock_user_1 (creator) should succeed.
    - mock_user_2 (non-creator) should fail with 403 Forbidden.
    """
    update_data = ActivityUpdate(title="Morning Running Club")
    
    # 1. Update as creator (mock_user_1) -> Should Succeed
    updated = update_existing_activity(db, mock_activity.id, update_data, mock_user_1)
    assert updated.title == "Morning Running Club"
    
    # 2. Update as non-creator (mock_user_2) -> Should Fail (403 Forbidden)
    with pytest.raises(HTTPException) as exc:
        update_existing_activity(db, mock_activity.id, update_data, mock_user_2)
        
    assert exc.value.status_code == 403
    assert "You do not have permission to modify this activity." in exc.value.detail


def test_only_creator_can_cancel_activity(db, mock_user_1, mock_user_2, mock_activity):
    """
    Verify that only the activity creator can cancel the activity.
    - mock_user_2 (non-creator) cancels -> Should Fail with 403.
    - mock_user_1 (creator) cancels -> Should Succeed.
    """
    # 1. Cancel as non-creator -> Should Fail
    with pytest.raises(HTTPException) as exc:
        cancel_existing_activity(db, mock_activity.id, mock_user_2)
    assert exc.value.status_code == 403
    assert "You do not have permission to modify this activity." in exc.value.detail
    
    # 2. Cancel as creator -> Should Succeed
    cancelled = cancel_existing_activity(db, mock_activity.id, mock_user_1)
    assert cancelled.status == ActivityStatus.CANCELLED.value


def test_only_creator_can_view_requests(db, mock_user_1, mock_user_2, mock_activity):
    """
    Verify that only the activity creator can view the list of participation requests.
    """
    req = ParticipationRequest(activity_id=mock_activity.id, user_id=mock_user_2.id, status=RequestStatus.PENDING.value)
    db.add(req)
    db.commit()

    # 1. View as creator -> Should Succeed
    reqs = list_requests(db, mock_activity.id, mock_user_1)
    assert len(reqs) == 1
    
    # 2. View as non-creator -> Should Fail (403)
    with pytest.raises(HTTPException) as exc:
        list_requests(db, mock_activity.id, mock_user_2)
        
    assert exc.value.status_code == 403
    assert "You do not have permission to manage this activity's requests." in exc.value.detail


def test_only_creator_can_approve_or_reject(db, mock_user_1, mock_user_2, mock_activity):
    """
    Verify that only the creator can approve/reject participation requests.
    """
    req = ParticipationRequest(activity_id=mock_activity.id, user_id=mock_user_2.id, status=RequestStatus.PENDING.value)
    db.add(req)
    db.commit()

    # 1. Attempt approval as non-creator (mock_user_2) -> Should Fail (403)
    with pytest.raises(HTTPException) as exc:
        approve_or_reject(db, mock_activity.id, req.id, RequestStatus.APPROVED.value, mock_user_2)
    assert exc.value.status_code == 403
    assert "You do not have permission to manage this activity's requests." in exc.value.detail
    
    # 2. Attempt approval as creator (mock_user_1) -> Should Succeed
    res = approve_or_reject(db, mock_activity.id, req.id, RequestStatus.APPROVED.value, mock_user_1)
    assert res.status == RequestStatus.APPROVED.value


def test_contact_info_visibility_rules(db, mock_user_1, mock_user_2, mock_user_3, mock_activity):
    """
    Verify that contact details are private and only visible after approval to the creator and participant.
    """
    req = ParticipationRequest(activity_id=mock_activity.id, user_id=mock_user_2.id, status=RequestStatus.PENDING.value)
    db.add(req)
    db.commit()

    # 1. Check contact info when PENDING -> Should Fail (403)
    with pytest.raises(HTTPException) as exc:
        get_contact_info(db, mock_activity.id, req.id, mock_user_1)
    assert exc.value.status_code == 403
    assert "Contact info is only visible after a request is approved." in exc.value.detail

    # Approve the request
    approve_or_reject(db, mock_activity.id, req.id, RequestStatus.APPROVED.value, mock_user_1)

    # 2. Check contact info as unrelated third party (mock_user_3) -> Should Fail (403)
    with pytest.raises(HTTPException) as exc:
        get_contact_info(db, mock_activity.id, req.id, mock_user_3)
    assert exc.value.status_code == 403
    assert "You do not have permission to view this contact info." in exc.value.detail

    # 3. Check contact info as creator -> Should Succeed, sees participant details
    info_for_creator = get_contact_info(db, mock_activity.id, req.id, mock_user_1)
    assert info_for_creator["participant_phone"] == "0987654321"
    assert info_for_creator["creator_phone"] is None  # Creator doesn't see their own phone in response

    # 4. Check contact info as approved participant -> Should Succeed, sees creator details
    info_for_participant = get_contact_info(db, mock_activity.id, req.id, mock_user_2)
    assert info_for_participant["creator_phone"] == "1234567890"
    assert info_for_participant["participant_phone"] is None


def test_cancel_request_success(db, mock_user_1, mock_user_2, mock_activity):
    """Verify that a user can cancel their own pending request."""
    req = ParticipationRequest(
        activity_id=mock_activity.id,
        user_id=mock_user_2.id,
        status=RequestStatus.PENDING.value
    )
    db.add(req)
    db.commit()

    # Cancel the request
    cancelled = cancel_request(db, mock_activity.id, req.id, mock_user_2)
    assert cancelled.id == req.id

    # Check that it is deleted from the database
    assert db.query(ParticipationRequest).filter(ParticipationRequest.id == req.id).first() is None


def test_cancel_request_failures(db, mock_user_1, mock_user_2, mock_user_3, mock_activity):
    """Verify various failure scenarios for cancelling requests."""
    req = ParticipationRequest(
        activity_id=mock_activity.id,
        user_id=mock_user_2.id,
        status=RequestStatus.PENDING.value
    )
    db.add(req)
    db.commit()

    # 1. Attempt to cancel someone else's request -> Should Fail (403)
    with pytest.raises(HTTPException) as exc:
        cancel_request(db, mock_activity.id, req.id, mock_user_3)
    assert exc.value.status_code == 403
    assert "You can only cancel your own requests." in exc.value.detail

    # 2. Attempt to cancel a non-existent request -> Should Fail (404)
    with pytest.raises(HTTPException) as exc:
        cancel_request(db, mock_activity.id, 99999, mock_user_2)
    assert exc.value.status_code == 404
    assert "Participation request not found." in exc.value.detail

    # 3. Attempt to cancel an approved request -> Should Fail (400)
    req.status = RequestStatus.APPROVED.value
    db.commit()
    with pytest.raises(HTTPException) as exc:
        cancel_request(db, mock_activity.id, req.id, mock_user_2)
    assert exc.value.status_code == 400
    assert "Cannot cancel a request that is already approved." in exc.value.detail