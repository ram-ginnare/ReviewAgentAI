from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.ai_review_service import AIReviewService
import backend.app.services.ai_review_service as ai_review_service_module

client = TestClient(app)


def create_session_and_rate(rating: int) -> str:
    session_response = client.post(
        "/api/v1/reviews/session",
        json={"business_slug": "abc-restaurant"},
    )
    assert session_response.status_code == 201
    session_id = session_response.json()["session_id"]

    rating_response = client.post(
        f"/api/v1/reviews/session/{session_id}/rating",
        json={"rating": rating},
    )
    assert rating_response.status_code == 200
    return session_id


def test_positive_reviews_fallback_when_groq_fails(monkeypatch):
    class FailingGroq:
        def __init__(self, api_key=None):
            raise RuntimeError("simulated Groq outage")

    class FakeSettings:
        groq_api_key = "test-key"
        groq_model = "test-model"

    monkeypatch.setattr(ai_review_service_module, "Groq", FailingGroq)
    monkeypatch.setattr(ai_review_service_module, "settings", FakeSettings())

    result = AIReviewService.generate_reviews(
        rating=5,
        selected_preferences=["Professional staff", "Reliable Service"],
        customer_comment="Fast and friendly service",
        fallback_comments=[
            "Great experience with professional staff and reliable service.",
            "Really enjoyed the visit with friendly service.",
            "Excellent overall experience.",
        ],
    )

    assert result.source == "fallback"
    assert len(result.reviews) == 3
    assert all(result.reviews)


def test_private_feedback_is_saved_and_returns_acknowledgement():
    session_id = create_session_and_rate(2)

    response = client.post(
        f"/api/v1/reviews/session/{session_id}/private-feedback",
        json={"comments": "The staff was slow and the wait was too long."},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["session_id"] == session_id
    assert body["rating"] == 2
    assert body["complaint_id"] > 0
    assert body["status"] == "completed"
    assert body["acknowledgement"]

    from sqlalchemy import select
    from backend.app.db.database import SessionLocal
    from backend.app.models.notification import Notification

    with SessionLocal() as db:
        notification = db.scalar(
            select(Notification).where(
                Notification.complaint_id == body["complaint_id"]
            )
        )
        assert notification is not None
        assert notification.type == "PRIVATE_FEEDBACK"
        assert notification.status == "PENDING"


def test_private_feedback_rejects_positive_rating():
    session_id = create_session_and_rate(5)

    response = client.post(
        f"/api/v1/reviews/session/{session_id}/private-feedback",
        json={"comments": "Everything was great."},
    )

    assert response.status_code == 409
    assert "ratings 1 to 3" in response.json()["detail"]
