from pydantic import BaseModel, Field

class AdvancedAnalyticsResponse(BaseModel):
    business_id: int
    business_slug: str
    period_days: int
    total_events: int
    event_counts: dict[str,int]
    rating_counts: dict[str,int]
    positive_reviews: int
    negative_reviews: int
    positive_ratio: float = Field(ge=0, le=100)
    negative_ratio: float = Field(ge=0, le=100)
    complaints: int
    google_handoffs: int
    google_handoff_rate: float = Field(ge=0, le=100)
    source_counts: dict[str,int]
    ai_usage: int
    fallback_usage: int
    monthly_trend: list[dict]
