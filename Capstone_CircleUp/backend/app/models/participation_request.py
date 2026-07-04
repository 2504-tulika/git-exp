"""
ParticipationRequest model.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.constants import RequestStatus


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
    
    @property
    def user_name(self) -> str | None:
        return self.user.name if self.user else None
    def __repr__(self) -> str:
        return (
            f"<ParticipationRequest id={self.id} "
            f"activity={self.activity_id} "
            f"user={self.user_id} "
            f"status={self.status!r}>"
        )