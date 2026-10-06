from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

class ReviewEvent(Base):
    __tablename__ = "review_events"
    __table_args__ = (
        Index("ix_review_events_business_created", "business_id", "created_at"),
        Index("ix_review_events_type", "event_type"),
        Index("ix_review_events_business_type_created", "business_id", "event_type", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    event_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    business = relationship("Business", back_populates="review_events")
