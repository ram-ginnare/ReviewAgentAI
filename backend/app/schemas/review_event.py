from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewEventCreate(BaseModel):
    event_type: str = Field(..., min_length=2, max_length=50)
    rating: int | None = Field(default=None, ge=1, le=5)
    event_metadata: dict | None = None


class ReviewEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    event_type: str
    rating: int | None
    event_metadata: dict | None
    created_at: datetime


class SocialLinkClickResponse(BaseModel):
    business_id: int
    social_link_id: int
    platform: str
    url: str
    event_id: int
