"""
Activity model.
`status` uses a Python enum for type safety in application code but is
stored as a plain VARCHAR in Postgres — avoids needing an ALTER TYPE
migration every time a new status is added.

`max_participants` is nullable (SRS marks it "Good to Have"). When null,
the activity has no capacity limit and will never auto-transition to Full.
"""

from datetime import date, datetime, time, timezone

from sqlalchemy import DATE, TIME, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.constants import ActivityStatus, ActivityCategory

class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    activity_date: Mapped[date] = mapped_column(DATE, nullable=False)
    activity_time: Mapped[time] = mapped_column(TIME, nullable=False)
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default=ActivityStatus.OPEN.value,
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

    creator: Mapped["User"] = relationship("User", back_populates="activities")
    participation_requests: Mapped[list["ParticipationRequest"]] = relationship(
        "ParticipationRequest", back_populates="activity", cascade="all, delete-orphan"
    )

    @property
    def creator_name(self) -> str | None:
        return self.creator.name if self.creator else None
    def __repr__(self) -> str:
        return f"<Activity id={self.id} title={self.title!r} status={self.status!r}>"
