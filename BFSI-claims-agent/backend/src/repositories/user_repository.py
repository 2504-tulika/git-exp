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

    def get_by_customer_id(self, customer_id):
        """Look up a login account by its customer_id, which is also the login ID."""
        return self.db.query(User).filter(User.customer_id == customer_id).first()

    def customer_already_registered(self, customer_id):
        """
        Check if the customer already has a login account.
        """
        return self.get_by_customer_id(customer_id) is not None

    def create_user(self, customer_id, password_hash):
        """
        Create a new login account for an existing customer_id.
        """
        return self.create(customer_id=customer_id, password_hash=password_hash)
