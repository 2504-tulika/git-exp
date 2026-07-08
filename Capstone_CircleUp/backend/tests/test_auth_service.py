import pytest
from fastapi import HTTPException
from app.services.auth_service import register_user, login_user
from app.schemas.user import UserRegister

def test_register_user_success(db):
    """Verify registering a valid user hashes their password and persists them."""
    register_data = UserRegister(
        name="John Doe",
        email="john.doe@gmail.com",
        password="Password123!",
        phone="9876543210",
        gender="Male",
        city="San Francisco",
        bio="Hello world",
        social_handle="@john_doe"
    )
    user = register_user(db, register_data)
    assert user.id is not None
    assert user.name == "John Doe"
    assert user.email == "john.doe@gmail.com"
    assert user.password_hash != "Password123!"  # Password securely hashed!


def test_register_duplicate_email_error(db, mock_user_1):
    """Verify registering a user with an already existing email raises a 409 conflict."""
    register_data_1 = UserRegister(
        name="Duplicate Test",
        email="dup@gmail.com",
        password="Password123!",
        phone="9876543210",
        gender="Male",
        city="Chicago"
    )
    register_user(db, register_data_1)

    # Registering again with the same email must fail with 409
    with pytest.raises(HTTPException) as exc:
        register_user(db, register_data_1)
    
    assert exc.value.status_code == 409
    assert "An account with this email already exists." in exc.value.detail


def test_login_user_success(db):
    """Verify login with correct credentials returns a token and user."""
    register_data = UserRegister(
        name="Login Success User",
        email="loginsuccess@gmail.com",
        password="Password123!",
        phone="9876543210",
        gender="Other",
        city="New York"
    )
    register_user(db, register_data)

    res = login_user(db, "loginsuccess@gmail.com", "Password123!")
    assert "access_token" in res
    assert res["token_type"] == "bearer"
    assert res["user"].email == "loginsuccess@gmail.com"


def test_login_user_invalid_email(db):
    """Verify login with non-existent email raises 401 Unauthorized."""
    with pytest.raises(HTTPException) as exc:
        login_user(db, "nonexistent@gmail.com", "Password123!")
    
    assert exc.value.status_code == 401
    assert "Invalid email." in exc.value.detail


def test_login_user_invalid_password(db):
    """Verify login with correct email but incorrect password raises 401 Unauthorized."""
    register_data = UserRegister(
        name="Wrong Pass User",
        email="wrongpass@gmail.com",
        password="Password123!",
        phone="9876543210",
        gender="Male",
        city="Miami"
    )
    register_user(db, register_data)

    with pytest.raises(HTTPException) as exc:
        login_user(db, "wrongpass@gmail.com", "IncorrectPass!")
    
    assert exc.value.status_code == 401
    assert "Password is invalid." in exc.value.detail