from sqlalchemy import inspect

from backend.app.db.base import Base
from backend.app.db.database import engine
from backend.app.db.seed import seed_demo_data
from backend.app.models import (
    Business,
    SocialLink,
    LocalComplaint,
    GeneratedPositiveReview,
    ReviewEvent,
    Notification,
    ReviewSession,
    FallbackReviewComment,
    User,
    Subscription,
    BillingPayment,
    AuditLog,
    SubscriptionPlan,
)

EXPECTED_TABLES = {
    "businesses",
    "social_links",
    "local_complaints",
    "generated_positive_reviews",
    "review_events",
    "notifications",
    "review_sessions",
    "fallback_review_comments",
    "users",
    "subscriptions",
    "billing_payments",
    "audit_logs",
    "subscription_plans",
}

def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    missing_tables = EXPECTED_TABLES - existing_tables

    if missing_tables:
        raise RuntimeError(
            f"Database initialization failed. Missing tables: {sorted(missing_tables)}"
        )

    seed_demo_data()

if __name__ == "__main__":
    initialize_database()
    print("reviewagentai database initialized successfully.")
