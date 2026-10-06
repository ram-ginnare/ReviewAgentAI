from datetime import datetime
from pydantic import BaseModel

from backend.app.schemas.analytics import AnalyticsResponse


class DashboardComplaintItem(BaseModel):
    id: int
    rating: int
    comments: str
    status: str
    notification_status: str
    created_at: datetime


class DashboardResponse(BaseModel):
    business_id: int
    business_slug: str
    business_name: str
    category: str | None
    logo_url: str | None
    analytics: AnalyticsResponse
    complaint_counts: dict[str, int]
    recent_complaints: list[DashboardComplaintItem]
