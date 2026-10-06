from backend.app.schemas.dashboard import DashboardResponse
from backend.app.schemas.notification import NotificationResponse
class OwnerDashboardResponse(DashboardResponse):
    plan: str
    subscription_status: str
    unread_notifications: int
