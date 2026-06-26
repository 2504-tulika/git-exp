"""
ParticipationRequest model.

The unique constraint on (activity_id, user_id) enforces the SRS rule
"users cannot submit duplicate participation requests" at the database
level — a second request for the same activity from the same user will
raise an IntegrityError before application code even runs.

Contact visibility rule: once status = 'approved', the service layer
permits both parties to see each other's contact info. This model itself
has no visibility logic — it only stores state.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ParticipationRequest(Base):
    __tablename__ = "participation_requests"

    __table_args__ = (
        UniqueConstraint(
            "activity_id", "user_id", name="uq_participation_activity_user"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default=RequestStatus.PENDING.value,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    activity: Mapped["Activity"] = relationship(
        "Activity", back_populates="participation_requests"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="participation_requests"
    )

    def __repr__(self) -> str:
        return (
            f"<ParticipationRequest id={self.id} "
            f"activity={self.activity_id} "
            f"user={self.user_id} "
            f"status={self.status!r}>"
        )