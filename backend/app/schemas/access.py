from datetime import datetime

from pydantic import BaseModel, Field


class CustomerAccessRequest(BaseModel):
    source: str = Field(default="direct", min_length=2, max_length=20)


class CustomerAccessResponse(BaseModel):
    session_id: str
    business_id: str
    business_slug: str
    business_name: str
    source: str
    status: str
    created_at: datetime
