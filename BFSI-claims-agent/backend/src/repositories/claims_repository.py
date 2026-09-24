"""
Claims history queries -- used by both the "claim history" MCP tool
(context for a claim) and the "fraud risk" MCP tool (frequency, past
flags, patterns).
"""

from src.repositories.base_repository import BaseRepository
from src.repositories.models import ClaimsHistory
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ClaimsRepository(BaseRepository):
    def __init__(self, db):
        super().__init__(db, ClaimsHistory)

    def get_claims_for_customer(self, customer_id):
        """Every past claim this customer has filed, across all their policies."""
        return (
            self.db.query(ClaimsHistory)
            .filter(ClaimsHistory.customer_id == customer_id)
            .order_by(ClaimsHistory.incident_date.desc())
            .all()
        )

    def get_claims_for_policy(self, policy_id):
        """Every past claim filed under this policy (could be by more than one customer)."""
        return (
            self.db.query(ClaimsHistory)
            .filter(ClaimsHistory.policy_id == policy_id)
            .order_by(ClaimsHistory.incident_date.desc())
            .all()
        )

    def count_claims_for_customer(self, customer_id):
        """
        How many claims this customer has filed in total, across every
        policy they hold -- the fraud tool's "unusually frequent claims"
        signal is built on this.
        """
        return (
            self.db.query(ClaimsHistory)
            .filter(ClaimsHistory.customer_id == customer_id)
            .count()
        )

    def has_prior_fraud_flag(self, customer_id):
        """Has this customer had any past claim flagged as a fraud risk?"""
        flagged = (
            self.db.query(ClaimsHistory)
            .filter(ClaimsHistory.customer_id == customer_id, ClaimsHistory.fraud_flag == True)  # noqa: E712
            .first()
        )
        return flagged is not None

    def create_claim(self, **fields):
        """Insert a new claim record (e.g. when a customer submits one through the app)."""
        return self.create(**fields)
