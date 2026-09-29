from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.schemas.auth_schema import LoginRequest, SignupRequest, TokenResponse, UserResponse
from src.services import auth_service
from src.services.auth_service import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create a new login account for an existing customer_id."""
    user = auth_service.signup(db, request)
    return user


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Verify credentials and issue a JWT access token."""
    access_token = auth_service.login(db, request)
    token_response = TokenResponse(access_token=access_token)
    return token_response


def get_current_user_dep(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(db, token)
    return user


