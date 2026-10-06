from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base

class Subscription(Base):
    __tablename__ = 'subscriptions'
    __table_args__ = (Index('ix_subscriptions_business_status','business_id','status'),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey('businesses.id', ondelete='CASCADE'), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(30), nullable=False, default='STARTER')
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='TRIALING')
    provider: Mapped[str] = mapped_column(String(30), nullable=False, default='MOCK')
    provider_customer_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    provider_subscription_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(default=False, server_default='0', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    business = relationship('Business', back_populates='subscription')

class BillingPayment(Base):
    __tablename__ = 'billing_payments'
    __table_args__ = (Index('ix_billing_payments_business_created','business_id','created_at'),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    business_id: Mapped[int] = mapped_column(ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False)
    plan: Mapped[str] = mapped_column(String(30), nullable=False)
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='INR')
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    provider: Mapped[str] = mapped_column(String(30), nullable=False, default='MOCK')
    provider_payment_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    receipt_reference: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
