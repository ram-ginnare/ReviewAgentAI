from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.main import app
from backend.app.db.database import SessionLocal
from backend.app.models.generated_review import GeneratedPositiveReview

client = TestClient(app)


def create_positive_session() -> str:
    session_response = client.post(
        "/api/v1/reviews/session",
        json={"business_slug": "reviewagentai"},
    )
    assert session_response.status_code == 201
    session_id = session_response.json()["session_id"]

    rating_response = client.post(
        f"/api/v1/reviews/session/{session_id}/rating",
        json={"rating": 5},
    )
    assert rating_response.status_code == 200
    return session_id


def create_generated_review(session_id: str) -> int:
    response = client.post(
        f"/api/v1/reviews/session/{session_id}/positive-reviews",
        json={"professional_staff": True, "customer_comment": "Fast, friendly, and absolutely delicious!"},
    )
    assert response.status_code == 200
    return response.json()["reviews"][0]["id"]


def test_select_generated_review_returns_google_url():
    session_id = create_positive_session()
    review_id = create_generated_review(session_id)

    response = client.post(
        f"/api/v1/reviews/session/{session_id}/google-review/select",
        json={"review_id": review_id},
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/140.0.0.0 Safari/537.36"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == session_id
    assert body["selected_review_id"] == review_id
    assert body["rating"] == 5
    assert body["review_text"]
    assert body["google_review_pc_url"].startswith(
        "https://search.google.com/local/writereview?placeid="
    )
    assert body["google_review_mob_url"] == "https://g.page/r/CQXyLImX75mfEBM/review"
    assert body["google_review_url"] == body["google_review_pc_url"]
    assert body["device_type"] == "desktop"
    assert body["status"] == "completed"

    with SessionLocal() as db:
        review = db.get(GeneratedPositiveReview, review_id)
        assert review is not None
        assert review.selected is True


def test_select_generated_review_rejects_negative_session():
    session_response = client.post(
        "/api/v1/reviews/session",
        json={"business_slug": "reviewagentai"},
    )
    assert session_response.status_code == 201
    session_id = session_response.json()["session_id"]

    rating_response = client.post(
        f"/api/v1/reviews/session/{session_id}/rating",
        json={"rating": 2},
    )
    assert rating_response.status_code == 200

    response = client.post(
        f"/api/v1/reviews/session/{session_id}/google-review/select",
        json={"review_id": 1},
    )

    assert response.status_code == 409
    assert "ratings 4 or 5" in response.json()["detail"]


def test_select_generated_review_rejects_review_from_other_business_or_rating():
    session_id = create_positive_session()
    review_id = create_generated_review(session_id)

    # Sanity check that the generated review exists and belongs to the expected business.
    with SessionLocal() as db:
        review = db.scalar(select(GeneratedPositiveReview).where(GeneratedPositiveReview.id == review_id))
        assert review is not None

    response = client.post(
        f"/api/v1/reviews/session/{session_id}/google-review/select",
        json={"review_id": 999999},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Generated review not found"


def test_select_generated_review_accepts_customer_edited_text():
    session_id = create_positive_session()
    review_id = create_generated_review(session_id)

    final_text = "The team was professional and the service was excellent. I would happily return."
    response = client.post(
        f"/api/v1/reviews/session/{session_id}/google-review/select",
        json={"review_id": review_id, "final_review_text": final_text},
    )

    assert response.status_code == 200
    assert response.json()["review_text"] == final_text

    with SessionLocal() as db:
        review = db.get(GeneratedPositiveReview, review_id)
        assert review.generated_review == final_text
