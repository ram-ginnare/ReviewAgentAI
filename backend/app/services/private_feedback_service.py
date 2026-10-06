from sqlalchemy.orm import Session

from backend.app.models.complaint import LocalComplaint
from backend.app.models.notification import Notification
from backend.app.models.review_session import ReviewSession
from backend.app.core.statuses import ReviewSessionStatus
from backend.app.services.ai_review_service import AIReviewService
from backend.app.services.review_session_service import ReviewSessionService


class PrivateFeedbackService:

    @staticmethod
    def submit_feedback(
        db: Session,
        session_id: str,
        comments: str,
    ) -> tuple[ReviewSession, LocalComplaint, str]:
        review_session = ReviewSessionService.validate_active_session(db, session_id)

        if review_session.rating is None:
            raise ValueError("Review session has not been rated")

        if review_session.rating > 3:
            raise ValueError("Private feedback is available only for ratings 1 to 3")

        complaint = LocalComplaint(
            business_id=review_session.business_id,
            rating=review_session.rating,
            comments=comments.strip(),
            status="NEW",
            notification_status="PENDING",
        )

        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        notification = Notification(
            business_id=review_session.business_id,
            complaint_id=complaint.id,
            type="PRIVATE_FEEDBACK",
            status="PENDING",
            message=f"New private customer feedback received for a {review_session.rating}/5 rating.",
        )
        db.add(notification)
        db.commit()

        acknowledgement = AIReviewService.generate_complaint_acknowledgement(comments)

        # Mark the review session as completed without adding/changing DB columns.
        review_session.status = ReviewSessionStatus.COMPLETED
        db.commit()
        db.refresh(review_session)

        return review_session, complaint, acknowledgement
