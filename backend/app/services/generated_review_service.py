from dataclasses import dataclass
import re
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.business import Business
from backend.app.models.fallback_review_comment import FallbackReviewComment
from backend.app.models.generated_review import GeneratedPositiveReview
from backend.app.models.review_session import ReviewSession
from backend.app.services.ai_review_service import AIReviewService, ReviewGenerationResult
from backend.app.services.review_session_service import ReviewSessionService


PREFERENCE_LABELS = {
    "professional_staff": "Professional staff",
    "reliable_service": "Reliable Service",
    "good_ambiance": "Good Ambiance",
    "affordable_pricing": "Affordable Pricing",
}

PREFERENCE_TERMS = {
    "professional_staff": {"professional", "staff", "friendly", "team", "helpful", "courteous"},
    "reliable_service": {"reliable", "service", "dependable", "smooth", "quick", "efficient", "prompt"},
    "good_ambiance": {"ambiance", "atmosphere", "welcoming", "comfortable", "pleasant", "environment"},
    "affordable_pricing": {"affordable", "pricing", "price", "value", "reasonable", "budget", "money"},
}


@dataclass(frozen=True)
class ReviewInput:
    selected_preferences: list[str]
    customer_comment: str


class GeneratedReviewService:

    @staticmethod
    def _get_fallback_comments(db: Session, business_id: int, rating: int) -> list[FallbackReviewComment]:
        return db.scalars(
            select(FallbackReviewComment)
            .where(
                FallbackReviewComment.business_id == business_id,
                FallbackReviewComment.rating == rating,
                FallbackReviewComment.enabled.is_(True),
            )
            .order_by(FallbackReviewComment.display_order, FallbackReviewComment.id)
        ).all()

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token
            for token in re.findall(r"[a-zA-Z]{3,}", text.lower())
            if token not in {"the", "and", "was", "with", "for", "this", "that", "very", "had", "have"}
        }

    @staticmethod
    def _score_comment(comment: str, query_terms: set[str], query_text: str) -> float:
        comment_tokens = GeneratedReviewService._tokens(comment)
        if not comment_tokens or not query_terms:
            return 0.0

        overlap = len(comment_tokens & query_terms)
        score = overlap * 10.0

        # Reward close phrase/word similarity for free-text input without requiring
        # exact wording in the fallback comment.
        for query_token in query_terms:
            best_similarity = max(
                (SequenceMatcher(None, query_token, comment_token).ratio() for comment_token in comment_tokens),
                default=0.0,
            )
            if best_similarity >= 0.80:
                score += 2.0

        normalized_query = " ".join(GeneratedReviewService._tokens(query_text))
        if normalized_query and normalized_query in comment.lower():
            score += 8.0

        return score

    @staticmethod
    def _match_fallback_comments(
        comments: list[FallbackReviewComment],
        selected_keys: list[str],
        customer_comment: str,
    ) -> list[FallbackReviewComment]:
        query_terms = set(GeneratedReviewService._tokens(customer_comment))
        for key in selected_keys:
            query_terms.update(PREFERENCE_TERMS[key])

        scored = [
            (
                GeneratedReviewService._score_comment(row.comment, query_terms, customer_comment),
                row.display_order,
                row,
            )
            for row in comments
        ]
        scored.sort(key=lambda item: (-item[0], item[1], item[2].id))

        # If the business has too few comments or no lexical match, still return
        # the best configured comments rather than an empty review list.
        return [row for _, _, row in scored[:3]]

    @staticmethod
    def build_review_input(
        professional_staff: bool,
        reliable_service: bool,
        good_ambiance: bool,
        affordable_pricing: bool,
        customer_comment: str | None,
    ) -> ReviewInput:
        values = {
            "professional_staff": professional_staff,
            "reliable_service": reliable_service,
            "good_ambiance": good_ambiance,
            "affordable_pricing": affordable_pricing,
        }
        selected = [PREFERENCE_LABELS[key] for key, enabled in values.items() if enabled]
        comment = (customer_comment or "").strip()
        if not selected and not comment:
            raise ValueError("Select at least one checkbox or enter a customer comment")
        return ReviewInput(selected_preferences=selected, customer_comment=comment)

    @staticmethod
    def generate_positive_reviews(
        db: Session,
        session_id: str,
        professional_staff: bool,
        reliable_service: bool,
        good_ambiance: bool,
        affordable_pricing: bool,
        customer_comment: str | None,
    ) -> tuple[ReviewSession, list[GeneratedPositiveReview], ReviewGenerationResult, ReviewInput]:
        review_session = ReviewSessionService.validate_active_session(db, session_id)

        if review_session.rating is None:
            raise ValueError("Review session has not been rated")
        if review_session.rating < 4:
            raise ValueError("Positive reviews are available only for ratings 4 or 5")

        review_input = GeneratedReviewService.build_review_input(
            professional_staff,
            reliable_service,
            good_ambiance,
            affordable_pricing,
            customer_comment,
        )

        business = db.get(Business, int(review_session.business_id))
        if business is None:
            raise ValueError("Business not found")

        fallback_rows = GeneratedReviewService._get_fallback_comments(
            db, business.id, review_session.rating
        )
        if not fallback_rows:
            raise ValueError(
                f"No fallback review comments are configured for rating {review_session.rating}"
            )

        matched_rows = GeneratedReviewService._match_fallback_comments(
            fallback_rows,
            [key for key, enabled in {
                "professional_staff": professional_staff,
                "reliable_service": reliable_service,
                "good_ambiance": good_ambiance,
                "affordable_pricing": affordable_pricing,
            }.items() if enabled],
            review_input.customer_comment,
        )
        matched_comments = [row.comment for row in matched_rows]

        if business.prefer_ai_comments:
            result = AIReviewService.generate_reviews(
                rating=review_session.rating,
                selected_preferences=review_input.selected_preferences,
                customer_comment=review_input.customer_comment,
                fallback_comments=matched_comments,
            )
        else:
            result = ReviewGenerationResult(matched_comments, "fallback")

        combined_input = "; ".join(review_input.selected_preferences)
        if review_input.customer_comment:
            combined_input = f"{combined_input}; {review_input.customer_comment}" if combined_input else review_input.customer_comment

        reviews = [
            GeneratedPositiveReview(
                business_id=review_session.business_id,
                session_id=review_session.id,
                rating=review_session.rating,
                customer_input=combined_input,
                generated_review=generated_review,
            )
            for generated_review in result.reviews[:3]
        ]
        db.add_all(reviews)
        db.commit()
        for review in reviews:
            db.refresh(review)

        return review_session, reviews, result, review_input
