"""
User account queries -- used only by auth_service.py.
"""

from src.repositories.base_repository import BaseRepository
from src.repositories.models import User
from src.utils.logger import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, User)

    def get_by_username(self, username):
        """Look up a login account by username. Used to check login credentials."""
        return self.db.query(User).filter(User.username == username).first()

    def username_exists(self, username):
        return self.get_by_username(username) is not None

    def create_user(self, username, password_hash, customer_id):
        """
        Create a new login account, linked to an existing customer_id.
        auth_service.py hashes the password before calling this -- this
        repository never sees a plain-text password.
        """
        return self.create(username=username, password_hash=password_hash, customer_id=customer_id)
