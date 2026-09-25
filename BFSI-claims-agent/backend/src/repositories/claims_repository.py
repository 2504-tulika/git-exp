"""
Claims history queries -- used by both the "claim history" MCP tool
(context for a claim) and the "fraud risk" MCP tool (frequency, past
flags, patterns).
"""

from datetime import timedelta

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

    def get_claims_within_days_for_policy(self, policy_id, reference_date, days, exclude_claim_id=None):
        """
        Every claim on this policy whose incident_date falls within `days`
        days of reference_date, in either direction. This is what
        fraud_risk_tool.py uses to catch time-clustered claims -- e.g. two
        own-damage claims on the same vehicle "within the same week" --
        which count_claims_for_customer's plain total can't see on its own,
        since a customer with 3 claims spread over 2 years and a customer
        with 3 claims in 10 days both just show up as "3 claims".

        exclude_claim_id skips the claim being evaluated itself, so a
        claim already sitting in the database doesn't count itself as a
        neighbor of itself.
        """
        window_start = reference_date - timedelta(days=days)
        window_end = reference_date + timedelta(days=days)

        query = (
            self.db.query(ClaimsHistory)
            .filter(
                ClaimsHistory.policy_id == policy_id,
                ClaimsHistory.incident_date >= window_start,
                ClaimsHistory.incident_date <= window_end,
            )
        )
        if exclude_claim_id is not None:
            query = query.filter(ClaimsHistory.claim_id != exclude_claim_id)

        return query.order_by(ClaimsHistory.incident_date.asc()).all()

    def create_claim(self, **fields):
        """Insert a new claim record (e.g. when a customer submits one through the app)."""
        return self.create(**fields)
