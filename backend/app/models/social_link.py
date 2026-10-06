from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

class SocialLink(Base):
    __tablename__ = "social_links"
    __table_args__ = (Index("ix_social_links_business_platform", "business_id", "platform"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    business = relationship("Business", back_populates="social_links")
