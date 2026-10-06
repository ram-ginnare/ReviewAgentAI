from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.statuses import ReviewSessionStatus
from backend.app.models.business import Business
from backend.app.models.review_session import ReviewSession


class ReviewSessionService:

    @staticmethod
    def create_session(db: Session, business_slug: str) -> ReviewSession:
        business = db.scalar(select(Business).where(Business.slug == business_slug))
        if business is None:
            raise ValueError("Business not found")
        if business.status != "ACTIVE":
            raise ValueError("Business is not active")

        review_session = ReviewSession(business_id=business.id, status=ReviewSessionStatus.STARTED)
        db.add(review_session)
        db.commit()
        db.refresh(review_session)
        return review_session

    @staticmethod
    def get_session(db: Session, session_id: str) -> ReviewSession:
        review_session = db.get(ReviewSession, session_id)
        if review_session is None:
            raise ValueError("Review session not found")
        return review_session

    @staticmethod
    def expires_at(review_session: ReviewSession) -> datetime:
        created = review_session.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        return created + timedelta(minutes=settings.review_session_timeout_minutes)

    @classmethod
    def is_expired(cls, review_session: ReviewSession) -> bool:
        if review_session.status in {ReviewSessionStatus.COMPLETED, ReviewSessionStatus.EXPIRED}:
            return review_session.status == ReviewSessionStatus.EXPIRED
        return datetime.now(timezone.utc) >= cls.expires_at(review_session)

    @classmethod
    def validate_active_session(cls, db: Session, session_id: str) -> ReviewSession:
        review_session = cls.get_session(db, session_id)
        if review_session.status == ReviewSessionStatus.EXPIRED:
            raise ValueError("Review session has expired")
        if cls.is_expired(review_session):
            review_session.status = ReviewSessionStatus.EXPIRED
            db.commit()
            db.refresh(review_session)
            raise ValueError("Review session has expired")
        return review_session

    @classmethod
    def rate_session(cls, db: Session, session_id: str, rating: int) -> ReviewSession:
        review_session = cls.validate_active_session(db, session_id)

        if review_session.status != ReviewSessionStatus.STARTED:
            raise ValueError("Review session has already been rated")

        review_session.rating = rating
        review_session.status = ReviewSessionStatus.RATED
        db.commit()
        db.refresh(review_session)
        return review_session
