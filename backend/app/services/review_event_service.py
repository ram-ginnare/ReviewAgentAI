from sqlalchemy.orm import Session

from backend.app.models.business import Business
from backend.app.models.review_event import ReviewEvent
from backend.app.models.social_link import SocialLink


class ReviewEventService:
    ALLOWED_EVENT_TYPES = {
        "LANDING_PAGE_VIEW",
        "RATING_SELECTED",
        "AI_REVIEWS_GENERATED",
        "PRIVATE_FEEDBACK_SUBMITTED",
        "REVIEW_SELECTED",
        "GOOGLE_HANDOFF",
        "SOCIAL_LINK_CLICKED",
    }

    @classmethod
    def record_event(
        cls,
        db: Session,
        business_id: int,
        event_type: str,
        rating: int | None = None,
        event_metadata: dict | None = None,
    ) -> ReviewEvent:
        normalized_type = event_type.strip().upper()
        if normalized_type not in cls.ALLOWED_EVENT_TYPES:
            raise ValueError(
                "Unsupported event_type. Allowed values: "
                + ", ".join(sorted(cls.ALLOWED_EVENT_TYPES))
            )

        business = db.get(Business, business_id)
        if business is None:
            raise ValueError("Business not found")

        event = ReviewEvent(
            business_id=business_id,
            event_type=normalized_type,
            rating=rating,
            event_metadata=event_metadata,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @classmethod
    def record_business_event(
        cls,
        db: Session,
        slug: str,
        event_type: str,
        rating: int | None = None,
        event_metadata: dict | None = None,
    ) -> ReviewEvent:
        business = db.query(Business).filter(Business.slug == slug).first()
        if business is None:
            raise ValueError("Business not found")
        if business.status != "ACTIVE":
            raise ValueError("Business is not active")

        return cls.record_event(
            db=db,
            business_id=business.id,
            event_type=event_type,
            rating=rating,
            event_metadata=event_metadata,
        )

    @classmethod
    def record_social_link_click(
        cls,
        db: Session,
        slug: str,
        social_link_id: int,
        event_metadata: dict | None = None,
    ) -> tuple[SocialLink, ReviewEvent]:
        business = db.query(Business).filter(Business.slug == slug).first()
        if business is None:
            raise ValueError("Business not found")
        if business.status != "ACTIVE":
            raise ValueError("Business is not active")

        social_link = (
            db.query(SocialLink)
            .filter(
                SocialLink.id == social_link_id,
                SocialLink.business_id == business.id,
            )
            .first()
        )
        if social_link is None:
            raise ValueError("Social link not found")
        if not social_link.enabled:
            raise ValueError("Social link is disabled")

        metadata = dict(event_metadata or {})
        metadata.update(
            {
                "social_link_id": social_link.id,
                "platform": social_link.platform,
            }
        )

        event = cls.record_event(
            db=db,
            business_id=business.id,
            event_type="SOCIAL_LINK_CLICKED",
            event_metadata=metadata,
        )
        return social_link, event
