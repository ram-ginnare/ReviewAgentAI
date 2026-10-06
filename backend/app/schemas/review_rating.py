from datetime import datetime

from pydantic import BaseModel, Field


class ReviewRatingRequest(BaseModel):
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Customer rating from 1 to 5 stars",
    )


class ReviewRatingResponse(BaseModel):
    session_id: str
    business_id: str
    rating: int
    status: str
    next_step: str
    updated_at: datetime