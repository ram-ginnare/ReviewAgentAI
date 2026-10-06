from datetime import datetime, timedelta

from backend.app.core.config import settings
from backend.app.models.notification import Notification
from backend.app.services.notification_service import NotificationService
from backend.app.db.database import SessionLocal


def test_notification_lifecycle_and_retry():
    with SessionLocal() as db:
        notification = Notification(
            business_id=1,
            complaint_id=None,
            type="TEST",
            status="PENDING",
            message="test notification",
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        NotificationService.update_status(db, notification.id, "PROCESSING")
        assert notification.status == "PROCESSING"
        NotificationService.update_status(db, notification.id, "FAILED")
        assert notification.status == "FAILED"
        NotificationService.retry(db, notification.id)
        assert notification.status == "PENDING"
        NotificationService.update_status(db, notification.id, "PROCESSING")
        NotificationService.update_status(db, notification.id, "SENT")
        assert notification.status == "SENT"
        assert notification.sent_at is not None


def test_notification_api_available_for_business():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    client = TestClient(app)
    response = client.get("/api/v1/notifications/business/abc-restaurant")
    assert response.status_code == 200
    assert "items" in response.json()


def test_private_feedback_rate_limit_has_reasonable_configuration():
    assert settings.private_feedback_rate_limit_requests > 0
    assert settings.private_feedback_rate_limit_window_seconds > 0
