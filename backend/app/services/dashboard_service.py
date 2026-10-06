from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.business import Business
from backend.app.models.complaint import LocalComplaint
from backend.app.schemas.dashboard import DashboardComplaintItem
from backend.app.services.analytics_service import AnalyticsService


class DashboardService:
    @staticmethod
    def get_business_dashboard(db: Session, slug: str, days: int | None = None) -> dict:
        business = db.scalar(select(Business).where(Business.slug == slug))
        if business is None:
            raise ValueError("Business not found")
        if business.status != "ACTIVE":
            raise ValueError("Business is not active")

        analytics = AnalyticsService.get_business_analytics(db, slug, days)

        rows = db.execute(
            select(LocalComplaint.status, func.count(LocalComplaint.id))
            .where(LocalComplaint.business_id == business.id)
            .group_by(LocalComplaint.status)
        ).all()
        complaint_counts = {str(status): int(count) for status, count in rows}

        complaints = db.scalars(
            select(LocalComplaint)
            .where(LocalComplaint.business_id == business.id)
            .order_by(LocalComplaint.created_at.desc())
            .limit(10)
        ).all()

        recent_complaints = [
            DashboardComplaintItem(
                id=item.id,
                rating=item.rating,
                comments=item.comments,
                status=item.status,
                notification_status=item.notification_status,
                created_at=item.created_at,
            )
            for item in complaints
        ]

        return {
            "business_id": business.id,
            "business_slug": business.slug,
            "business_name": business.name,
            "category": business.category,
            "logo_url": business.logo_url,
            "analytics": analytics,
            "complaint_counts": complaint_counts,
            "recent_complaints": recent_complaints,
        }
