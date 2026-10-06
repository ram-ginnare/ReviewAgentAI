from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.business import Business
from backend.app.services.review_event_service import ReviewEventService
from backend.app.services.review_session_service import ReviewSessionService


class CustomerAccessService:
    ALLOWED_SOURCES = {"nfc", "qr", "direct"}

    @classmethod
    def create_customer_access(
        cls,
        db: Session,
        slug: str,
        source: str = "direct",
    ):
        normalized_source = source.strip().lower()

        if normalized_source not in cls.ALLOWED_SOURCES:
            raise ValueError(
                "Unsupported source. Allowed values: nfc, qr, direct"
            )

        business = db.scalar(
            select(Business).where(Business.slug == slug)
        )

        if business is None:
            raise ValueError("Business not found")

        if business.status != "ACTIVE":
            raise ValueError("Business is not active")
        if normalized_source == "nfc" and not business.nfc_enabled:
            raise ValueError("NFC access is disabled")
        if normalized_source == "qr" and not business.qr_enabled:
            raise ValueError("QR access is disabled")

        review_session = ReviewSessionService.create_session(
            db=db,
            business_slug=slug,
        )

        # Keep the access source in the existing event tracking table.
        ReviewEventService.record_business_event(
            db=db,
            slug=slug,
            event_type="LANDING_PAGE_VIEW",
            event_metadata={
                "source": normalized_source,
                "access_channel": normalized_source,
                "session_id": review_session.id,
            },
        )

        return business, review_session, normalized_source
