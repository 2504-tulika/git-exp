"""
Auth router — registration, login, and logout endpoints.

Routes are intentionally thin: they validate input (via Pydantic schemas),
call the appropriate service function, and return the response. No business
logic lives here.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import LoginResponse, UserLogin, UserRegister, UserResponse
from app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """
    Create a new CircleUp account.

    - Email must be unique across all users.
    - Password is hashed before storage, never stored in plain text.
    """
    user = register_user(db, data)
    return user


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login and receive access token",
)
def login(data: UserLogin, db: Session = Depends(get_db)):    
    """
    Authenticate with email and password.

    Returns a JWT access token valid for 90 minutes.
    Include this token in subsequent requests as:
    `Authorization: Bearer <token>`
    """
    result = login_user(db, data.email, data.password)
    return result


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout current user",
)
def logout():
    """
    Logout the current user.

    Since JWTs are stateless, logout is handled client-side by discarding
    the token. The server has no session to invalidate.
    """
    return {"message": "Logged out successfully."}