from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReviewSessionCreate(BaseModel):
    business_slug: str


class ReviewSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    business_id: str
    business_slug: str
    status: str
    created_at: datetime