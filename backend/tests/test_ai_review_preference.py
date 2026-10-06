from sqlalchemy import select
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.database import SessionLocal
from backend.app.models.business import Business
from backend.app.models.fallback_review_comment import FallbackReviewComment
import backend.app.services.ai_review_service as ai_review_service_module

client = TestClient(app)


def _new_session(slug: str, rating: int) -> str:
    response = client.post(
        "/api/v1/reviews/session",
        json={"business_slug": slug},
    )
    assert response.status_code == 201
    session_id = response.json()["session_id"]
    response = client.post(
        f"/api/v1/reviews/session/{session_id}/rating",
        json={"rating": rating},
    )
    assert response.status_code == 200
    return session_id


def test_business_exposes_prefer_ai_comments_flag():
    response = client.get("/api/v1/businesses/reviewagentai")
    assert response.status_code == 200
    assert response.json()["prefer_ai_comments"] is True


def test_ai_failure_returns_db_fallback_and_source(monkeypatch):
    class FailingGroq:
        def __init__(self, api_key=None):
            raise RuntimeError("simulated Groq outage")

    class FakeSettings:
        groq_api_key = "test-key"
        groq_model = "test-model"

    monkeypatch.setattr(ai_review_service_module, "Groq", FailingGroq)
    monkeypatch.setattr(ai_review_service_module, "settings", FakeSettings())

    session_id = _new_session("reviewagentai", 4)
    with SessionLocal() as db:
        fallback = db.scalar(
            select(FallbackReviewComment).where(
                FallbackReviewComment.business_id == 1,
                FallbackReviewComment.rating == 4,
                FallbackReviewComment.display_order == 1,
            )
        )
        assert fallback is not None
        expected_comment = fallback.comment

    response = client.post(
        f"/api/v1/reviews/session/{session_id}/positive-reviews",
        json={"reliable_service": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["generation_source"] == "fallback"
    assert len(body["reviews"]) == 3
    assert body["selected_preferences"] == ["Reliable Service"]
    assert body["reviews"][0]["generated_review"] == expected_comment


def test_business_can_prefer_database_comments_without_calling_groq(monkeypatch):
    with SessionLocal() as db:
        business = db.scalar(select(Business).where(Business.slug == "abc-restaurant"))
        assert business is not None
        assert business.prefer_ai_comments is False

    class ExplodingGroq:
        def __init__(self, api_key=None):
            raise AssertionError("Groq must not be called when PreferAIComments is false")

    monkeypatch.setattr(ai_review_service_module, "Groq", ExplodingGroq)

    session_id = _new_session("abc-restaurant", 5)
    response = client.post(
        f"/api/v1/reviews/session/{session_id}/positive-reviews",
        json={"good_ambiance": True, "customer_comment": "Great food"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["generation_source"] == "fallback"
    assert len(body["reviews"]) == 3
