from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_business_created", "business_id", "created_at"),
        Index("ix_notifications_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    complaint_id: Mapped[int | None] = mapped_column(ForeignKey("local_complaints.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", server_default="PENDING")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    business = relationship("Business", back_populates="notifications")
