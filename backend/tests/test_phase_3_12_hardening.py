from fastapi.testclient import TestClient
from sqlalchemy import inspect

from backend.app.main import app
from backend.app.core.rate_limit import InMemoryRateLimiter
from backend.app.db.database import engine, SessionLocal
from backend.app.models.generated_review import GeneratedPositiveReview

client = TestClient(app)


def _new_positive_session():
    session = client.post("/api/v1/reviews/session", json={"business_slug": "reviewagentai"})
    assert session.status_code == 201
    session_id = session.json()["session_id"]
    rating = client.post(f"/api/v1/reviews/session/{session_id}/rating", json={"rating": 5})
    assert rating.status_code == 200
    return session_id


def test_generated_review_is_linked_to_session():
    session_id = _new_positive_session()
    response = client.post(
        f"/api/v1/reviews/session/{session_id}/positive-reviews",
        json={"professional_staff": True},
    )
    assert response.status_code == 200
    review_id = response.json()["reviews"][0]["id"]
    with SessionLocal() as db:
        review = db.get(GeneratedPositiveReview, review_id)
        assert review.session_id == session_id


def test_generated_review_from_another_session_cannot_be_selected():
    session_a = _new_positive_session()
    session_b = _new_positive_session()
    generated = client.post(
        f"/api/v1/reviews/session/{session_a}/positive-reviews",
        json={"reliable_service": True},
    )
    assert generated.status_code == 200
    review_id = generated.json()["reviews"][0]["id"]

    response = client.post(
        f"/api/v1/reviews/session/{session_b}/google-review/select",
        json={"review_id": review_id},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Generated review does not belong to this session"


def test_error_response_contains_standard_code_and_detail():
    response = client.get("/api/v1/businesses/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["detail"] == "Business not found"
    assert body["code"] == "HTTP_404"


def test_ai_rate_limiter_allows_limit_then_blocks():
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)
    assert limiter.allow("test") is True
    assert limiter.allow("test") is True
    assert limiter.allow("test") is False
    limiter.reset()
    assert limiter.allow("test") is True


def test_hardening_indexes_and_constraints_exist():
    generated = {item["name"] for item in inspect(engine).get_indexes("generated_positive_reviews")}
    assert "ix_generated_reviews_session" in generated
    constraints = inspect(engine).get_check_constraints("generated_positive_reviews")
    assert any(item["name"] == "ck_generated_reviews_rating_1_5" for item in constraints)
