import uuid
from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.core.statuses import ReviewSessionStatus


class ReviewSession(Base):
    __tablename__ = "review_sessions"
    __table_args__ = (CheckConstraint("rating IS NULL OR rating BETWEEN 1 AND 5", name="ck_review_sessions_rating_1_5"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    business_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("businesses.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ReviewSessionStatus.STARTED, server_default=ReviewSessionStatus.STARTED,
    )

    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    generated_reviews = relationship("GeneratedPositiveReview", back_populates="session", cascade="all, delete-orphan")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )