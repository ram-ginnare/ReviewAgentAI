import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./reviewagentai.db",
    )

    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173",
    )

    groq_api_key: str | None = os.getenv("GROQ_API_KEY")

    # Long random secret used to sign authentication access tokens.
    auth_secret: str = os.getenv("AUTH_SECRET", "change-this-development-secret")
    demo_auth_seed: bool = os.getenv("DEMO_AUTH_SEED", "true").strip().lower() in {"1", "true", "yes"}

    groq_model: str = os.getenv(
        "GROQ_MODEL",
        "openai/gpt-oss-120b",
    )

    review_session_timeout_minutes: int = int(os.getenv("REVIEW_SESSION_TIMEOUT_MINUTES", "30"))
    ai_rate_limit_requests: int = int(os.getenv("AI_RATE_LIMIT_REQUESTS", "10"))
    ai_rate_limit_window_seconds: int = int(os.getenv("AI_RATE_LIMIT_WINDOW_SECONDS", "60"))
    private_feedback_rate_limit_requests: int = int(os.getenv("PRIVATE_FEEDBACK_RATE_LIMIT_REQUESTS", "5"))
    private_feedback_rate_limit_window_seconds: int = int(os.getenv("PRIVATE_FEEDBACK_RATE_LIMIT_WINDOW_SECONDS", "60"))
    business_api_key: str | None = os.getenv("BUSINESS_API_KEY")
    smtp_host: str | None = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str | None = os.getenv("SMTP_USERNAME")
    smtp_password: str | None = os.getenv("SMTP_PASSWORD")
    notification_from_email: str | None = os.getenv("NOTIFICATION_FROM_EMAIL")
    notification_to_email: str | None = os.getenv("NOTIFICATION_TO_EMAIL")
    billing_provider: str = os.getenv("BILLING_PROVIDER", "MOCK").upper()
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    audit_log_enabled: bool = os.getenv("AUDIT_LOG_ENABLED", "true").strip().lower() in {"1", "true", "yes"}

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
