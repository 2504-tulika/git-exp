"""add gender column and make phone required

Revision ID: a1b2c3d4e5f6
Revises: c669711c8eee
Create Date: 2026-07-01 00:00:00.000000

NOTE: this migration deletes all existing rows in `users` before
applying the NOT NULL constraints, since old demo users don't have
phone/gender values that satisfy the new required columns. This is a
local dev database with throwaway demo data — do NOT run this against
data you need to keep without backing it up first.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "c669711c8eee"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Wipe existing demo users — they predate phone/gender being required
    # and would violate the new NOT NULL constraints.
    op.execute("DELETE FROM participation_requests")
    op.execute("DELETE FROM activities")
    op.execute("DELETE FROM users")

    # Add gender column as required
    op.add_column("users", sa.Column("gender", sa.String(length=10), nullable=False))

    # Make phone required (was nullable before)
    op.alter_column(
        "users",
        "phone",
        existing_type=sa.String(length=20),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "phone",
        existing_type=sa.String(length=20),
        nullable=True,
    )
    op.drop_column("users", "gender")