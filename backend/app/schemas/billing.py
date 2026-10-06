from datetime import datetime
from pydantic import BaseModel, Field

PLANS = {
    'STARTER': {'price_paise': 99900, 'monthly_review_limit': 100},
    'PROFESSIONAL': {'price_paise': 249900, 'monthly_review_limit': 500},
    'BUSINESS': {'price_paise': 499900, 'monthly_review_limit': 2000},
}
class PlanResponse(BaseModel):
    code: str
    name: str
    price_paise: int
    monthly_review_limit: int
class SubscriptionResponse(BaseModel):
    plan: str
    status: str
    provider: str
    trial_ends_at: datetime | None
    current_period_start: datetime | None
    current_period_end: datetime | None
    cancel_at_period_end: bool
class CheckoutResponse(BaseModel):
    payment_id: int
    provider: str
    provider_order_id: str
    amount_paise: int
    currency: str
    receipt_reference: str
    status: str
class PaymentConfirmRequest(BaseModel):
    payment_id: int = Field(gt=0)
    success: bool = True
class BillingHistoryItem(BaseModel):
    id: int
    plan: str
    amount_paise: int
    currency: str
    status: str
    provider: str
    receipt_reference: str
    created_at: datetime
