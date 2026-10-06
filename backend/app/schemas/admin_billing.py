from datetime import datetime
from pydantic import BaseModel, Field


class AdminPlanResponse(BaseModel):
    id: int
    code: str
    name: str
    price_paise: int
    monthly_review_limit: int
    trial_days: int
    is_active: bool
    updated_at: datetime


class AdminPlanUpdateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price_paise: int = Field(ge=0, le=100_000_000)
    monthly_review_limit: int = Field(ge=1, le=10_000_000)
    trial_days: int = Field(ge=0, le=365)
    is_active: bool = True


class AdminSubscriptionItem(BaseModel):
    business_id: int
    business_name: str
    business_slug: str
    owner_email: str | None
    plan: str
    plan_name: str
    status: str
    provider: str
    trial_ends_at: datetime | None
    current_period_start: datetime | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
    plan_price_paise: int
    monthly_review_limit: int


class AdminSubscriptionUpdateRequest(BaseModel):
    plan: str = Field(min_length=1, max_length=30)
    status: str = Field(pattern=r'^(TRIALING|ACTIVE|PAST_DUE|CANCELLED)$')
    trial_ends_at: datetime | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    cancel_at_period_end: bool = False
