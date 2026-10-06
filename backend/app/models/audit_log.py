from datetime import datetime
from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        Index('ix_audit_logs_created', 'created_at'),
        Index('ix_audit_logs_user_created', 'user_id', 'created_at'),
        Index('ix_audit_logs_business_created', 'business_id', 'created_at'),
    )
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    business_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    request_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
