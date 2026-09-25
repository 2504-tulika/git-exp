"""
Policy-specific database queries.
"""

from src.repositories.base_repository import BaseRepository
from src.repositories.models import Policy, PolicyCustomer, Customer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PolicyRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, Policy)

    def get_customers_for_policy(self, policy_id):
        """List every customer independently covered under this policy."""
        return (
            self.db.query(Customer)
            .join(PolicyCustomer, PolicyCustomer.customer_id == Customer.customer_id)
            .filter(PolicyCustomer.policy_id == policy_id)
            .all()
        )

    def customer_owns_policy(self, customer_id, policy_id):
        """
        The core authorization check: is this customer actually one of the
        policyholders on this policy? Every claims/chat route that takes a
        policy_id must call this before doing anything else with it --
        otherwise a logged-in customer could look up someone else's policy
        just by guessing its ID.
        """
        link = (
            self.db.query(PolicyCustomer)
            .filter(
                PolicyCustomer.customer_id == customer_id,
                PolicyCustomer.policy_id == policy_id,
            )
            .first()
        )
        return link is not None
