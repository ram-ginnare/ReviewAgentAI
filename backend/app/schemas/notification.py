from datetime import datetime
from pydantic import BaseModel, Field


NOTIFICATION_STATUSES = {"PENDING", "PROCESSING", "SENT", "FAILED"}


class NotificationResponse(BaseModel):
    id: int
    business_id: int
    complaint_id: int | None
    type: str
    status: str
    message: str
    created_at: datetime
    sent_at: datetime | None


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int


class NotificationStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(PROCESSING|SENT|FAILED)$")


class NotificationRetryResponse(NotificationResponse):
    pass
