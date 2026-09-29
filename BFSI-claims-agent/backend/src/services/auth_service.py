from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.config import constants
from src.config.settings import settings
from src.exceptions.exceptions import (
    CustomerAlreadyRegisteredError,
    CustomerNotFoundError,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UsernameTakenError,
)
from src.repositories.customer_repository import CustomerRepository
from src.repositories.user_repository import UserRepository
from src.utils.logger import get_logger

logger = get_logger(__name__)

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_password(plain_password):
    """Hash a plain-text password for storage. Never store plain_password itself."""
    hashed = _pwd_context.hash(plain_password)
    return hashed


def verify_password(plain_password, password_hash):
    """True if plain_password matches the stored hash."""
    is_valid = _pwd_context.verify(plain_password, password_hash)
    return is_valid


def create_access_token(user):
    """Issue a JWT for an authenticated user, carrying username and customer_id."""
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry_minutes)
    payload = {"sub": user.username, "customer_id": user.customer_id, "exp": expire_at}
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token


def decode_access_token(token):
    """
    Decode and verify a JWT.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError(constants.TOKEN_EXPIRED)
    except jwt.InvalidTokenError:
        raise InvalidTokenError(constants.INVALID_TOKEN)
    return payload


def signup(db: Session, request):
    """
    Create a new login account for an existing customer.
    """
    customer_repo = CustomerRepository(db)
    user_repo = UserRepository(db)

    customer = customer_repo.get_by_id(request.customer_id)
    if customer is None:
        logger.warning(f"Signup failed: customer_id {request.customer_id} not found")
        raise CustomerNotFoundError(constants.CUSTOMER_NOT_FOUND)

    if user_repo.customer_already_registered(request.customer_id):
        logger.warning(f"Signup failed: customer_id {request.customer_id} already has an account")
        raise CustomerAlreadyRegisteredError(constants.CUSTOMER_ALREADY_REGISTERED)

    if user_repo.username_exists(request.username):
        logger.warning(f"Signup failed: username '{request.username}' already taken")
        raise UsernameTakenError(constants.USERNAME_TAKEN)

    password_hash = hash_password(request.password)
    user = user_repo.create_user(
        username=request.username, password_hash=password_hash, customer_id=request.customer_id
    )
    logger.info(f"New account created: username={user.username}, customer_id={user.customer_id}")
    return user


def login(db: Session, request):
    """
    Verify username/password and issue a JWT. request is a
    schemas.auth_schema.LoginRequest. Raises InvalidCredentialsError for
    both an unknown username and a wrong password -- deliberately the
    same exception for both, see module docstring.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(request.username)

    if user is None or not verify_password(request.password, user.password_hash):
        logger.warning(f"Login failed for username '{request.username}'")
        raise InvalidCredentialsError(constants.INVALID_CREDENTIALS)

    access_token = create_access_token(user)
    logger.info(f"Login succeeded: username={user.username}")
    return access_token


def get_current_user(db: Session, token: str):
    """
    Resolve the logged-in User from a bearer token.
    """
    payload = decode_access_token(token)

    username = payload.get("sub")
    if username is None:
        raise InvalidTokenError(constants.INVALID_TOKEN)

    user = UserRepository(db).get_by_username(username)
    if user is None:
        raise InvalidTokenError(constants.INVALID_TOKEN)

    return user


