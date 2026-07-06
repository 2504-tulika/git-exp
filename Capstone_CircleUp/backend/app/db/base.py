"""
SQLAlchemy declarative base.

All ORM models inherit from `Base`. Kept in its own module (separate from
session.py) so Alembic can import it without pulling in the engine/session
machinery.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass