"""
Activity-related enums and constants.
"""

import enum


class ActivityStatus(str, enum.Enum):
    OPEN      = "open"
    FULL      = "full"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityCategory(str, enum.Enum):
    SPORTS = "sports"
    SOCIAL = "social"
    STUDY  = "study"
    TRAVEL = "travel"
    FOOD   = "food"
    OTHER  = "other"