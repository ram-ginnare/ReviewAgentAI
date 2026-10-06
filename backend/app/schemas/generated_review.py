from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class PositiveReviewRequest(BaseModel):
    professional_staff: bool = Field(False, description="Customer highlights professional staff")
    reliable_service: bool = Field(False, description="Customer highlights reliable service")
    good_ambiance: bool = Field(False, description="Customer highlights good ambiance")
    affordable_pricing: bool = Field(False, description="Customer highlights affordable pricing")
    customer_comment: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional additional customer comment",
    )

    @model_validator(mode="after")
    def validate_at_least_one_input(self):
        if not any(
            [
                self.professional_staff,
                self.reliable_service,
                self.good_ambiance,
                self.affordable_pricing,
                bool((self.customer_comment or "").strip()),
            ]
        ):
            raise ValueError(
                "Select at least one checkbox or enter a customer comment"
            )
        if self.customer_comment:
            self.customer_comment = self.customer_comment.strip()
        return self


class GeneratedReviewItem(BaseModel):
    id: int
    generated_review: str
    selected: bool
    created_at: datetime


class PositiveReviewResponse(BaseModel):
    session_id: str
    business_id: str
    rating: int
    generation_source: str
    selected_preferences: list[str]
    customer_comment: str | None
    reviews: list[GeneratedReviewItem]
