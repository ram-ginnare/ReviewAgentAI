from datetime import datetime

from pydantic import BaseModel, Field


class SelectReviewRequest(BaseModel):
    review_id: int = Field(..., gt=0, description="ID of the generated review to select")
    final_review_text: str | None = Field(
        default=None, min_length=3, max_length=2000,
        description="Optional customer-edited final review text",
    )


class GoogleReviewSelectionResponse(BaseModel):
    session_id: str
    business_id: str
    rating: int
    selected_review_id: int
    review_text: str
    google_review_pc_url: str
    google_review_mob_url: str
    google_review_url: str
    device_type: str
    status: str
    updated_at: datetime
