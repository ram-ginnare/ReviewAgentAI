from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def _new_session(slug: str, rating: int) -> str:
    response = client.post("/api/v1/reviews/session", json={"business_slug": slug})
    assert response.status_code == 201
    session_id = response.json()["session_id"]
    response = client.post(f"/api/v1/reviews/session/{session_id}/rating", json={"rating": rating})
    assert response.status_code == 200
    return session_id


def test_positive_review_requires_checkbox_or_comment():
    session_id = _new_session("abc-restaurant", 5)
    response = client.post(
        f"/api/v1/reviews/session/{session_id}/positive-reviews",
        json={},
    )
    assert response.status_code == 422


def test_database_fallback_has_no_placeholders(monkeypatch):
    from backend.app.services import ai_review_service as module

    class ExplodingGroq:
        def __init__(self, api_key=None):
            raise AssertionError("Groq must not be called")

    monkeypatch.setattr(module, "Groq", ExplodingGroq)
    session_id = _new_session("abc-restaurant", 5)
    response = client.post(
        f"/api/v1/reviews/session/{session_id}/positive-reviews",
        json={"professional_staff": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["generation_source"] == "fallback"
    assert len(body["reviews"]) == 3
    assert all("{customer_input}" not in item["generated_review"] for item in body["reviews"])
