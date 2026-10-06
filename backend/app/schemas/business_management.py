from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class BusinessProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=100)
    logo_url: str | None = Field(default=None, max_length=1000)
    welcome_message: str | None = Field(default=None, max_length=1000)

class BrandingUpdate(BaseModel):
    brand_primary_color: str = Field(pattern=r'^#[0-9A-Fa-f]{6}$')
    brand_secondary_color: str = Field(pattern=r'^#[0-9A-Fa-f]{6}$')

class ReviewSettingsUpdate(BaseModel):
    prefer_ai_comments: bool
    google_review_pc_url: str = Field(min_length=1, max_length=2000)
    google_review_mob_url: str = Field(min_length=1, max_length=2000)
    nfc_enabled: bool
    qr_enabled: bool
    customer_settings: dict[str, object] = Field(default_factory=dict)

class SocialLinkCreate(BaseModel):
    platform: str = Field(min_length=1, max_length=30)
    url: str = Field(min_length=1, max_length=2000)
    display_order: int = Field(default=0, ge=0, le=1000)
    enabled: bool = True

class SocialLinkUpdate(SocialLinkCreate):
    pass

class BusinessSettingsResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None
    category: str | None
    logo_url: str | None
    welcome_message: str | None
    brand_primary_color: str
    brand_secondary_color: str
    prefer_ai_comments: bool
    google_review_pc_url: str
    google_review_mob_url: str
    nfc_enabled: bool
    qr_enabled: bool
    customer_settings: dict[str, object]
    updated_at: datetime
