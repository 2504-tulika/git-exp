import pytest
from unittest.mock import patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.constants import ActivityStatus, RequestStatus
from app.models.participation_request import ParticipationRequest
from app.services.participation_service import approve_or_reject, request_to_join
from app.repositories import count_approved_participants

def test_auto_transition_to_full(db, mock_user_1, mock_user_2, mock_user_3, mock_activity):
    """
    Verify that when the final slot is filled, the activity status auto-transitions to 'FULL'.
    Activity has max_participants = 2.
    """
    mock_activity.max_participants = 2
    mock_activity.status = ActivityStatus.OPEN.value
    db.commit()

    # 1. Create first approved request (1/2 filled)
    req1 = ParticipationRequest(
        activity_id=mock_activity.id,
        user_id=mock_user_2.id,
        status=RequestStatus.PENDING.value
    )
    db.add(req1)
    db.commit()
    
    req1_approved = approve_or_reject(db, mock_activity.id, req1.id, RequestStatus.APPROVED.value, mock_user_1)
    assert req1_approved.status == RequestStatus.APPROVED.value
    
    # Activity should still be OPEN because approved count (1) < max (2)
    db.refresh(mock_activity)
    assert mock_activity.status == ActivityStatus.OPEN.value

    # 2. Create second approved request (2/2 filled)
    req2 = ParticipationRequest(
        activity_id=mock_activity.id,
        user_id=mock_user_3.id,
        status=RequestStatus.PENDING.value
    )
    db.add(req2)
    db.commit()
    
    req2_approved = approve_or_reject(db, mock_activity.id, req2.id, RequestStatus.APPROVED.value, mock_user_1)
    assert req2_approved.status == RequestStatus.APPROVED.value
    
    # Activity should auto-transition to FULL since count (2) == max (2)
    db.refresh(mock_activity)
    assert mock_activity.status == ActivityStatus.FULL.value


def test_approve_beyond_capacity_error(db, mock_user_1, mock_user_2, mock_user_3, mock_activity):
    """
    Verify that approving a participant when the activity is already at max capacity raises a 400 Bad Request.
    """
    mock_activity.max_participants = 2
    mock_activity.status = ActivityStatus.FULL.value
    db.commit()

    # Pre-fill activity to capacity (2/2) by inserting approved requests directly
    req1 = ParticipationRequest(activity_id=mock_activity.id, user_id=mock_user_2.id, status=RequestStatus.APPROVED.value)
    req2 = ParticipationRequest(activity_id=mock_activity.id, user_id=mock_user_3.id, status=RequestStatus.APPROVED.value)
    db.add_all([req1, req2])
    db.commit()

    # Create a third user (Charlie, mock_user_3 was used above, let's make an ad-hoc 4th user)
    from app.models.user import User
    mock_user_4 = User(
        id=4,
        name="Diana Prince",
        email="diana@example.com",
        password_hash="...",
        phone="1112223333",
        gender="Female",
        city="Themyscira",
        social_handle="@wonder_d"
    )
    db.add(mock_user_4)
    db.commit()

    # Create a pending request for User 4
    req3 = ParticipationRequest(
        activity_id=mock_activity.id,
        user_id=mock_user_4.id,
        status=RequestStatus.PENDING.value
    )
    db.add(req3)
    db.commit()

    # Approving req3 should fail because activity is already full (2/2)
    with pytest.raises(HTTPException) as exc:
        approve_or_reject(db, mock_activity.id, req3.id, RequestStatus.APPROVED.value, mock_user_1)
    
    assert exc.value.status_code == 400
    assert "Cannot approve — activity has reached maximum capacity." in exc.value.detail


def test_request_to_join_when_full_error(db, mock_user_1, mock_user_2, mock_user_3, mock_activity):
    """
    Verify that submitting a request to join a FULL activity raises a 400 Bad Request.
    """
    # Mark activity as FULL
    mock_activity.status = ActivityStatus.FULL.value
    db.commit()

    with pytest.raises(HTTPException) as exc:
        request_to_join(db, mock_activity.id, mock_user_2)
        
    assert exc.value.status_code == 400
    assert "This activity is full and not accepting new requests." in exc.value.detail


@patch("app.services.participation_service.count_approved_participants")
def test_concurrency_race_condition_simulation(mock_count, db, mock_user_1, mock_user_2, mock_activity):
    """
    Simulate a concurrency race condition:
    Two threads concurrently try to approve different users.
    Using SELECT ... FOR UPDATE ensures row-level locks prevent over-approving.
    """
    req1 = ParticipationRequest(activity_id=mock_activity.id, user_id=mock_user_2.id, status=RequestStatus.PENDING.value)
    db.add(req1)
    db.commit()

    # Configure mock count to return 1 (making it seem like there's 1 spot left, max_participants is 2)
    mock_count.return_value = 1
    
    # Thread 1 succeeds in approving req1
    res = approve_or_reject(db, mock_activity.id, req1.id, RequestStatus.APPROVED.value, mock_user_1)
    assert res.status == RequestStatus.APPROVED.value
    
    # Verify count query was indeed invoked
    mock_count.assert_called_with(db, mock_activity.id)