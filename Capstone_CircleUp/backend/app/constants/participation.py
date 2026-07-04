"""
Participation request enums and constants.
"""

import enum


class RequestStatus(str, enum.Enum):
    PENDING  = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"