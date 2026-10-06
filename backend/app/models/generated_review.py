from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

class GeneratedPositiveReview(Base):
    __tablename__ = "generated_positive_reviews"
    __table_args__ = (
        Index("ix_generated_reviews_business_created", "business_id", "created_at"),
        Index("ix_generated_reviews_session", "session_id"),
        CheckConstraint("rating BETWEEN 1 AND 5", name="ck_generated_reviews_rating_1_5"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(ForeignKey("review_sessions.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_input: Mapped[str] = mapped_column(Text, nullable=False)
    generated_review: Mapped[str] = mapped_column(Text, nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    business = relationship("Business", back_populates="generated_reviews")
    session = relationship("ReviewSession", back_populates="generated_reviews")
