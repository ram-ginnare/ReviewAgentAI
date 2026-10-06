from datetime import datetime
from sqlalchemy import Boolean, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base


class SubscriptionPlan(Base):
    __tablename__ = 'subscription_plans'
    __table_args__ = (Index('ix_subscription_plans_active', 'is_active'),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_review_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    trial_days: Mapped[int] = mapped_column(Integer, nullable=False, default=14, server_default='14')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default='1')
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
