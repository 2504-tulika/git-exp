"""
Customer-specific database queries. Extra methods on top of what
BaseRepository already gives us for free (get_by_id, get_all, create,
update, delete).
"""

from src.repositories.base_repository import BaseRepository
from src.repositories.models import Customer, PolicyCustomer, Policy
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CustomerRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Customer)

    def get_policies_for_customer(self, customer_id):
        """
        List every policy this customer holds. Goes through the
        policy_customers link table, since one customer can have several
        policies (and each of those policies might also have other,
        unrelated customers on it -- we only care about this customer's
        side of the link here).
        """
        return (
            self.db.query(Policy)
            .join(PolicyCustomer, PolicyCustomer.policy_id == Policy.policy_id)
            .filter(PolicyCustomer.customer_id == customer_id)
            .all()
        )
