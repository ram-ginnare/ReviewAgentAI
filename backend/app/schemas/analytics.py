from pydantic import BaseModel, Field


class AnalyticsResponse(BaseModel):
    business_id: int
    business_slug: str
    period_days: int | None
    total_events: int
    event_counts: dict[str, int]
    rating_counts: dict[str, int]
    landing_page_views: int
    rating_selections: int
    ai_reviews_generated: int
    reviews_selected: int
    google_handoffs: int
    private_feedback_submitted: int
    social_link_clicks: int
    google_handoff_rate: float = Field(ge=0, le=100)
