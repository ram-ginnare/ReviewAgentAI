from datetime import datetime
from pydantic import BaseModel
class OwnerNotification(BaseModel):
    id: int
    complaint_id: int | None
    type: str
    status: str
    message: str
    created_at: datetime
    sent_at: datetime | None
    complaint_status: str | None = None
class OwnerNotificationList(BaseModel):
    items: list[OwnerNotification]
    total: int
    unread: int
