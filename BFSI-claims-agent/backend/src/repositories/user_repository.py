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

    def get_by_customer_id(self, customer_id):
        """Look up a login account by the customer_id it's linked to, if one exists."""
        return self.db.query(User).filter(User.customer_id == customer_id).first()

    def customer_already_registered(self, customer_id):
        """
        Check if the customer already has a login account.
        """
        return self.get_by_customer_id(customer_id) is not None

    def create_user(self, username, password_hash, customer_id):
        """
        Create a new login account, linked to an existing customer_id.
        """
        return self.create(username=username, password_hash=password_hash, customer_id=customer_id)
