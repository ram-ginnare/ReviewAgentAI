from datetime import datetime
from pydantic import BaseModel


class ReviewSessionStatusResponse(BaseModel):
    session_id: str
    business_id: str
    status: str
    rating: int | None
    expires_at: datetime
    expired: bool


class ReviewFlowResponse(BaseModel):
    session_id: str
    business_id: str
    business_slug: str
    business_name: str
    status: str
    rating: int | None
    next_step: str
    expires_at: datetime
    expired: bool
