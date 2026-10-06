from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class AdminOwnerOption(BaseModel):
    id: int
    email: str
    full_name: str
    business_id: int | None
    is_active: bool

class AdminSocialLink(BaseModel):
    id: int | None = None
    platform: str = Field(min_length=1, max_length=30)
    url: str = Field(min_length=1, max_length=2000)
    display_order: int = Field(default=0, ge=0, le=1000)
    enabled: bool = True

class AdminBusinessCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=100)
    logo_url: str | None = Field(default=None, max_length=1000)
    google_review_pc_url: str = Field(min_length=1, max_length=2000)
    google_review_mob_url: str = Field(min_length=1, max_length=2000)
    status: str = Field(default='ACTIVE', pattern=r'^(ACTIVE|INACTIVE)$')
    prefer_ai_comments: bool = True
    brand_primary_color: str = Field(default='#4f46e5', pattern=r'^#[0-9A-Fa-f]{6}$')
    brand_secondary_color: str = Field(default='#312e81', pattern=r'^#[0-9A-Fa-f]{6}$')
    welcome_message: str | None = Field(default=None, max_length=1000)
    nfc_enabled: bool = True
    qr_enabled: bool = True
    customer_settings: dict[str, object] = Field(default_factory=dict)
    social_links: list[AdminSocialLink] = Field(default_factory=list)
    owner_id: int | None = None

class AdminBusinessUpdate(AdminBusinessCreate):
    pass

class AdminBusinessItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    description: str | None
    category: str | None
    logo_url: str | None
    google_review_pc_url: str
    google_review_mob_url: str
    status: str
    prefer_ai_comments: bool
    brand_primary_color: str
    brand_secondary_color: str
    welcome_message: str | None
    nfc_enabled: bool
    qr_enabled: bool
    customer_settings: dict[str, object]
    owner_id: int | None
    owner_email: str | None
    owner_name: str | None
    plan: str
    plan_name: str
    subscription_status: str
    review_count: int
    complaint_count: int
    average_rating: float | None
    social_links: list[AdminSocialLink]
    created_at: datetime
    updated_at: datetime

class AdminBusinessListResponse(BaseModel):
    businesses: list[AdminBusinessItem]
    owners: list[AdminOwnerOption]
