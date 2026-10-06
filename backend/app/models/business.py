from datetime import datetime
from sqlalchemy import Boolean, DateTime, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

class Business(Base):
    __tablename__ = "businesses"
    __table_args__ = (
        Index("ix_businesses_slug", "slug", unique=True),
        Index("ix_businesses_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    google_review_pc_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    google_review_mob_url: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE", server_default="ACTIVE")
    # Business preference: True = try Groq AI first; False = use database comments.
    prefer_ai_comments: Mapped[bool] = mapped_column(
        "PreferAIComments", Boolean, nullable=False, default=True, server_default="1"
    )
    brand_primary_color: Mapped[str] = mapped_column(String(20), nullable=False, default="#4f46e5", server_default="#4f46e5")
    brand_secondary_color: Mapped[str] = mapped_column(String(20), nullable=False, default="#312e81", server_default="#312e81")
    welcome_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    nfc_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    qr_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    customer_settings_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    social_links = relationship("SocialLink", back_populates="business", cascade="all, delete-orphan")
    complaints = relationship("LocalComplaint", back_populates="business", cascade="all, delete-orphan")
    generated_reviews = relationship("GeneratedPositiveReview", back_populates="business", cascade="all, delete-orphan")
    fallback_review_comments = relationship("FallbackReviewComment", back_populates="business", cascade="all, delete-orphan")
    review_events = relationship("ReviewEvent", back_populates="business", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="business", cascade="all, delete-orphan")
    users = relationship("User", back_populates="business")
    subscription = relationship("Subscription", back_populates="business", uselist=False, cascade="all, delete-orphan")
