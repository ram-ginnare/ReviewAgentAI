from datetime import datetime

from pydantic import BaseModel, Field


class PrivateFeedbackRequest(BaseModel):
    comments: str = Field(..., min_length=3, max_length=2000)


class PrivateFeedbackResponse(BaseModel):
    session_id: str
    business_id: str
    complaint_id: int
    rating: int
    status: str
    acknowledgement: str
    created_at: datetime
