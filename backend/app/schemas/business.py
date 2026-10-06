from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class SocialLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    platform: str
    url: str
    display_order: int
    enabled: bool

class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    logo_url: str | None
    description: str | None
    category: str | None
    google_review_pc_url: str
    google_review_mob_url: str
    status: str
    prefer_ai_comments: bool
    brand_primary_color: str
    brand_secondary_color: str
    welcome_message: str | None
    nfc_enabled: bool
    qr_enabled: bool
    created_at: datetime
    updated_at: datetime
    social_links: list[SocialLinkResponse] = Field(default_factory=list)
