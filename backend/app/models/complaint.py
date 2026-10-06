from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

class LocalComplaint(Base):
    __tablename__ = "local_complaints"
    __table_args__ = (
        Index("ix_local_complaints_business_created", "business_id", "created_at"),
        Index("ix_local_complaints_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    comments: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="NEW", server_default="NEW")
    notification_status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING", server_default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    business = relationship("Business", back_populates="complaints")
