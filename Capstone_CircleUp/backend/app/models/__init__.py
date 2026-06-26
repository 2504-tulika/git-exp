"""
Import all models here so that:
  1. Alembic's env.py only needs to import this module to see every table.
  2. SQLAlchemy's relationship resolution works without circular imports.
"""

from app.models.activity import Activity, ActivityCategory, ActivityStatus  # noqa: F401
from app.models.participation_request import ParticipationRequest, RequestStatus  # noqa: F401
from app.models.user import User  # noqa: F401