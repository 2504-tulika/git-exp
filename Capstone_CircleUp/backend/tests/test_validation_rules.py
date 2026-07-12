import pytest
from datetime import date, time, timedelta
from pydantic import ValidationError
from fastapi import status

from app.schemas.activity import ActivityCreate, ActivityUpdate

def test_activity_create_valid():
    """Verify clean validation with valid parameters."""
    future_date = date.today() + timedelta(days=5)
    activity = ActivityCreate(
        title="Weekend Football",
        category="Sports",
        location="Central Park Turf",
        activity_date=future_date,
        activity_time=time(16, 0),
        max_participants=10
    )
    assert activity.title == "Weekend Football"
    assert activity.max_participants == 10


def test_activity_create_empty_title():
    """Verify title validation strips whitespace and fails on empty strings."""
    future_date = date.today() + timedelta(days=5)
    with pytest.raises(ValidationError) as exc:
        ActivityCreate(
            title="   ", # Empty spaces
            category="Sports",
            location="Central Park Turf",
            activity_date=future_date,
            activity_time=time(16, 0),
            max_participants=10
        )
    assert "Title cannot be empty." in str(exc.value)


def test_activity_create_past_date():
    """Verify activity date cannot be set in the past."""
    past_date = date.today() - timedelta(days=1)
    with pytest.raises(ValidationError) as exc:
        ActivityCreate(
            title="Past Jogging Session",
            category="Sports",
            location="Golden Gate Park",
            activity_date=past_date,
            activity_time=time(10, 0),
            max_participants=10
        )
    assert "Activity date must be in the future." in str(exc.value)


def test_activity_create_past_time_today():
    """
    Verify scheduling an activity for today with a past time
    fails the combined date-time future constraint.
    """
    from datetime import datetime
    today = date.today()
    # Subtract 1 hour from current time to guarantee a past time today
    past_hour = (datetime.now() - timedelta(hours=1)).time()
    
    with pytest.raises(ValidationError) as exc:
        ActivityCreate(
            title="Late Running",
            category="Sports",
            location="Local Track",
            activity_date=today,
            activity_time=past_hour,
            max_participants=10
        )
    assert "Activity date and time must be in the future." in str(exc.value)


def test_activity_create_invalid_participants():
    """Verify max_participants must be greater than zero."""
    future_date = date.today() + timedelta(days=5)
    with pytest.raises(ValidationError) as exc:
        ActivityCreate(
            title="Zero Participant Run",
            category="Sports",
            location="Gym room",
            activity_date=future_date,
            activity_time=time(12, 0),
            max_participants=0 # 0 or negative is invalid
        )
    assert any(msg in str(exc.value) for msg in [
        "Maximum participants must be greater than zero.",
        "Input should be greater than 0"
    ])


def test_activity_create_location_empty():
    """Verify location must be stripped and cannot be empty."""
    future_date = date.today() + timedelta(days=5)
    with pytest.raises(ValidationError) as exc:
        ActivityCreate(
            title="Yoga Session",
            category="Health",
            location="   ", # empty spaces
            activity_date=future_date,
            activity_time=time(12, 0),
            max_participants=10
        )
    assert any(msg in str(exc.value) for msg in [
        "Location cannot be empty.",
        "String should have at least 5 characters"
    ])


def test_api_validation_errors(auth_client, mock_user_1):
    """
    Verify endpoint layer returns structured 422 Unprocessable Entity
    when invalid data parameters are received.
    """
    past_date = date.today() - timedelta(days=2)
    response = auth_client.post(
        "/api/v1/activities/",
        json={
            "title": "", # Invalid!
            "category": "Fun",
            "location": "Park", # Too short (min_length=5)
            "activity_date": past_date.isoformat(), # Invalid!
            "activity_time": "15:00:00",
            "max_participants": -5 # Invalid!
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    errors = response.json()["detail"]
    assert len(errors) > 0