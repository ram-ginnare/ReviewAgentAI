from datetime import datetime, timezone
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.business import Business
from backend.app.models.complaint import LocalComplaint
from backend.app.models.notification import Notification


ALLOWED_TRANSITIONS = {
    "PENDING": {"PROCESSING", "FAILED"},
    "PROCESSING": {"SENT", "FAILED"},
    "FAILED": {"PENDING"},
    "SENT": set(),
}


class NotificationService:
    @staticmethod
    def _business(db: Session, slug: str) -> Business:
        business = db.scalar(select(Business).where(Business.slug == slug))
        if business is None:
            raise ValueError("Business not found")
        if business.status != "ACTIVE":
            raise ValueError("Business is not active")
        return business

    @staticmethod
    def list_for_business(db: Session, slug: str, status_filter: str | None, limit: int) -> tuple[list[Notification], int]:
        business = NotificationService._business(db, slug)
        query = select(Notification).where(Notification.business_id == business.id)
        count_query = select(func.count(Notification.id)).where(Notification.business_id == business.id)
        if status_filter:
            query = query.where(Notification.status == status_filter)
            count_query = count_query.where(Notification.status == status_filter)
        items = db.scalars(query.order_by(Notification.created_at.desc()).limit(limit)).all()
        total = int(db.scalar(count_query) or 0)
        return items, total

    @staticmethod
    def update_status(db: Session, notification_id: int, new_status: str) -> Notification:
        notification = db.get(Notification, notification_id)
        if notification is None:
            raise ValueError("Notification not found")
        allowed = ALLOWED_TRANSITIONS.get(notification.status, set())
        if new_status not in allowed:
            raise ValueError(f"Invalid notification status transition: {notification.status} -> {new_status}")

        notification.status = new_status
        if new_status == "SENT":
            notification.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
        elif new_status in {"PENDING", "FAILED", "PROCESSING"}:
            if new_status != "SENT":
                notification.sent_at = None

        if notification.complaint_id:
            complaint = db.get(LocalComplaint, notification.complaint_id)
            if complaint is not None:
                complaint.notification_status = new_status

        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def retry(db: Session, notification_id: int) -> Notification:
        return NotificationService.update_status(db, notification_id, "PENDING")
