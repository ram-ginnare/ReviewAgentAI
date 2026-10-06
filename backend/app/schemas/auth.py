from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=200)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Enter a valid email address")
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str
    role: str
    business_id: int | None
    is_active: bool
    created_at: datetime


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)


class CreateUserRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=200)
    full_name: str = Field(min_length=1, max_length=200)
    role: str
    business_id: int | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        value = value.strip().lower()
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Enter a valid email address")
        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        value = value.strip().upper()
        if value not in {"ADMIN", "BUSINESS_OWNER"}:
            raise ValueError("Role must be ADMIN or BUSINESS_OWNER")
        return value
