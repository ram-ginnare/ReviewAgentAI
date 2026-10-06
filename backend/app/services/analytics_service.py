from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.business import Business
from backend.app.models.review_event import ReviewEvent


class AnalyticsService:
    @staticmethod
    def get_business_analytics(
        db: Session,
        slug: str,
        days: int | None = None,
    ) -> dict:
        business = db.scalar(select(Business).where(Business.slug == slug))
        if business is None:
            raise ValueError("Business not found")
        if business.status != "ACTIVE":
            raise ValueError("Business is not active")

        conditions = [ReviewEvent.business_id == business.id]
        if days is not None:
            since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
            conditions.append(ReviewEvent.created_at >= since)

        rows = db.execute(
            select(ReviewEvent.event_type, func.count(ReviewEvent.id))
            .where(*conditions)
            .group_by(ReviewEvent.event_type)
        ).all()
        event_counts = {event_type: int(count) for event_type, count in rows}

        rating_rows = db.execute(
            select(ReviewEvent.rating, func.count(ReviewEvent.id))
            .where(*conditions, ReviewEvent.rating.is_not(None))
            .group_by(ReviewEvent.rating)
        ).all()
        rating_counts = {str(rating): int(count) for rating, count in rating_rows}

        total_events = sum(event_counts.values())
        google_handoffs = event_counts.get("GOOGLE_HANDOFF", 0)
        rating_selections = event_counts.get("RATING_SELECTED", 0)
        google_handoff_rate = round((google_handoffs / rating_selections) * 100, 2) if rating_selections else 0.0

        return {
            "business_id": business.id,
            "business_slug": business.slug,
            "period_days": days,
            "total_events": total_events,
            "event_counts": event_counts,
            "rating_counts": rating_counts,
            "landing_page_views": event_counts.get("LANDING_PAGE_VIEW", 0),
            "rating_selections": rating_selections,
            "ai_reviews_generated": event_counts.get("AI_REVIEWS_GENERATED", 0),
            "reviews_selected": event_counts.get("REVIEW_SELECTED", 0),
            "google_handoffs": google_handoffs,
            "private_feedback_submitted": event_counts.get("PRIVATE_FEEDBACK_SUBMITTED", 0),
            "social_link_clicks": event_counts.get("SOCIAL_LINK_CLICKED", 0),
            "google_handoff_rate": google_handoff_rate,
        }
