from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.business import Business
from backend.app.core.statuses import ReviewSessionStatus
from backend.app.models.generated_review import GeneratedPositiveReview
from backend.app.models.review_session import ReviewSession
from backend.app.services.review_session_service import ReviewSessionService
from backend.app.services.device_detection import get_google_review_url


class GoogleReviewService:
    @staticmethod
    def select_review(
        db: Session,
        session_id: str,
        review_id: int,
        final_review_text: str | None = None,
    ) -> tuple[ReviewSession, GeneratedPositiveReview, Business]:
        review_session = ReviewSessionService.validate_active_session(db, session_id)

        if review_session.rating is None:
            raise ValueError("Review session has not been rated")

        if review_session.rating < 4:
            raise ValueError("Google review selection is available only for ratings 4 or 5")
        if review_session.status == ReviewSessionStatus.COMPLETED:
            raise ValueError("Review session has already been completed")

        review = db.get(GeneratedPositiveReview, review_id)
        if review is None:
            raise ValueError("Generated review not found")

        if review.session_id != review_session.id:
            raise ValueError("Generated review does not belong to this session")

        if str(review.business_id) != str(review_session.business_id):
            raise ValueError("Generated review does not belong to this business")

        if review.rating != review_session.rating:
            raise ValueError("Generated review does not match the session rating")

        business_id = _business_id_as_int(review_session.business_id)
        business = db.scalar(select(Business).where(Business.id == business_id))
        if business is None:
            raise ValueError("Business not found")

        if business.status != "ACTIVE":
            raise ValueError("Business is not active")

        if not business.google_review_pc_url:
            raise ValueError("Google PC review URL is not configured")

        if not business.google_review_mob_url:
            raise ValueError("Google mobile review URL is not configured")

        if final_review_text is not None:
            final_review_text = final_review_text.strip()
            if len(final_review_text) < 3:
                raise ValueError("Final review text must contain at least 3 characters")
            review.generated_review = final_review_text

        # Only one review can be the final selection for a session.
        db.query(GeneratedPositiveReview).filter(
            GeneratedPositiveReview.session_id == review_session.id,
            GeneratedPositiveReview.id != review.id,
        ).update({GeneratedPositiveReview.selected: False}, synchronize_session=False)
        review.selected = True
        review_session.status = ReviewSessionStatus.COMPLETED
        db.commit()
        db.refresh(review)
        db.refresh(review_session)

        return review_session, review, business


    @staticmethod
    def get_review_url(business: Business, user_agent: str | None) -> tuple[str, str]:
        return get_google_review_url(business, user_agent)


def _business_id_as_int(business_id: str) -> int:
    try:
        return int(business_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid business ID in review session") from exc
