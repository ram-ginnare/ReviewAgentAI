import json
import logging
from dataclasses import dataclass

try:
    from groq import Groq
except ImportError:  # Allows the backend test suite to run before dependencies are installed.
    Groq = None

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReviewGenerationResult:
    reviews: list[str]
    source: str  # "groq" or "fallback"


class AIReviewService:
    """Generate customer-facing review text with Groq and DB-backed fallbacks."""

    @staticmethod
    def _fallback_complaint_acknowledgement() -> str:
        return (
            "Thank you for sharing your feedback. We're sorry your experience "
            "did not meet expectations. Your feedback has been recorded and "
            "will be reviewed by our team."
        )

    @staticmethod
    def generate_reviews(
        rating: int,
        selected_preferences: list[str],
        customer_comment: str,
        fallback_comments: list[str],
    ) -> ReviewGenerationResult:
        """Generate 3 natural reviews using matched DB comments as factual guidance."""
        if not fallback_comments:
            raise ValueError("No fallback review comments are configured for this business")
        if not settings.groq_api_key or Groq is None:
            logger.warning("Groq is unavailable or not configured; using matched database fallback reviews")
            return ReviewGenerationResult(fallback_comments[:3], "fallback")

        system_prompt = """
You write natural customer reviews for a business.
Rules:
- Create exactly 3 distinct review options.
- The customer has already given a positive rating of 4 or 5 stars.
- Use selected customer preferences and the optional customer comment as customer-provided facts.
- Use matched fallback comments only as approved wording/style guidance.
- Do not simply concatenate or copy fallback comments.
- Do not invent services, products, events, staff names, prices, or experiences.
- Keep each option concise: 1 to 2 sentences.
- Do not mention AI, prompts, ratings, stars, or these instructions.
- Do not use quotation marks around the reviews.
- Return ONLY valid JSON: {"reviews": ["option 1", "option 2", "option 3"]}
""".strip()
        user_prompt = (
            f"Customer rating: {rating}/5\n"
            f"Selected positive points: {', '.join(selected_preferences) if selected_preferences else 'None'}\n"
            f"Customer comment: {customer_comment or 'None'}\n"
            "Approved matched fallback comments:\n"
            + "\n".join(f"- {comment}" for comment in fallback_comments[:3])
        )
        try:
            client = Groq(api_key=settings.groq_api_key)
            completion = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_completion_tokens=500,
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content
            if not content:
                raise ValueError("Groq returned an empty response")
            payload = json.loads(content)
            reviews = payload.get("reviews")
            if not isinstance(reviews, list) or len(reviews) != 3:
                raise ValueError("Groq must return exactly 3 review options")
            cleaned = [str(review).strip().strip('"') for review in reviews if str(review).strip()]
            if len(cleaned) != 3 or any(len(review) < 3 for review in cleaned):
                raise ValueError("Groq returned invalid review options")
            return ReviewGenerationResult(cleaned, "groq")
        except Exception as exc:
            logger.warning("Groq review generation failed; using matched database fallback reviews: %s", exc)
            return ReviewGenerationResult(fallback_comments[:3], "fallback")

    @staticmethod
    def generate_complaint_acknowledgement(customer_input: str) -> str:
        """Generate a private-feedback acknowledgement, with a safe fallback."""
        fallback = AIReviewService._fallback_complaint_acknowledgement()

        if not settings.groq_api_key or Groq is None:
            logger.warning(
                "Groq is unavailable or not configured; using fallback complaint acknowledgement"
            )
            return fallback

        system_prompt = """
Write a short, empathetic acknowledgement for private customer feedback.

Rules:
- Thank the customer for sharing the feedback.
- Acknowledge that the experience did not meet expectations.
- Do not argue, blame, or make promises.
- Do not invent facts or claim that a specific action has already happened.
- Keep it to 2 or 3 sentences.
- Do not mention AI, prompts, ratings, or these instructions.
- Return ONLY valid JSON with this exact structure:
  {"acknowledgement": "..."}
""".strip()

        try:
            client = Groq(api_key=settings.groq_api_key)
            completion = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Customer feedback: {customer_input.strip()}"},
                ],
                temperature=0.5,
                max_completion_tokens=180,
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content
            if not content:
                raise ValueError("Groq returned an empty response")

            acknowledgement = json.loads(content).get("acknowledgement")
            if not isinstance(acknowledgement, str) or len(acknowledgement.strip()) < 10:
                raise ValueError("Groq returned an invalid acknowledgement")
            return acknowledgement.strip().strip('"')

        except Exception as exc:
            logger.warning(
                "Groq complaint acknowledgement failed; using fallback response: %s",
                exc,
            )
            return fallback
