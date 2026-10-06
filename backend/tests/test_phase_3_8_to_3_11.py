from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from backend.app.db.database import SessionLocal
from backend.app.main import app
from backend.app.models.business import Business
from backend.app.models.review_event import ReviewEvent
from backend.app.models.review_session import ReviewSession

client = TestClient(app)


def get_business(slug="reviewagentai"):
    with SessionLocal() as db:
        return db.query(Business).filter(Business.slug == slug).first()


def test_phase_3_8_analytics_counts_events():
    business = get_business()
    assert business is not None

    with SessionLocal() as db:
        db.add_all([
            ReviewEvent(business_id=business.id, event_type="LANDING_PAGE_VIEW"),
            ReviewEvent(business_id=business.id, event_type="RATING_SELECTED", rating=5),
            ReviewEvent(business_id=business.id, event_type="RATING_SELECTED", rating=4),
            ReviewEvent(business_id=business.id, event_type="GOOGLE_HANDOFF", rating=5),
            ReviewEvent(business_id=business.id, event_type="SOCIAL_LINK_CLICKED"),
        ])
        db.commit()

    response = client.get(f"/api/v1/analytics/business/{business.slug}")
    assert response.status_code == 200
    body = response.json()
    assert body["total_events"] >= 5
    assert body["landing_page_views"] >= 1
    assert body["rating_selections"] >= 2
    assert body["google_handoffs"] >= 1
    assert body["social_link_clicks"] >= 1
    assert body["rating_counts"]["5"] >= 1


def test_phase_3_8_analytics_rejects_invalid_days():
    response = client.get("/api/v1/analytics/business/reviewagentai?days=0")
    assert response.status_code == 422


def test_phase_3_9_dashboard_returns_business_metrics_and_complaints():
    business = get_business()
    assert business is not None

    response = client.get(f"/api/v1/dashboard/business/{business.slug}")
    assert response.status_code == 200
    body = response.json()
    assert body["business_slug"] == business.slug
    assert body["business_name"] == business.name
    assert "analytics" in body
    assert "complaint_counts" in body
    assert "recent_complaints" in body


def test_phase_3_9_dashboard_can_limit_analytics_period():
    response = client.get("/api/v1/dashboard/business/reviewagentai?days=30")
    assert response.status_code == 200
    assert response.json()["analytics"]["period_days"] == 30


def test_phase_3_10_expired_session_is_rejected_for_rating():
    business = get_business()
    assert business is not None

    with SessionLocal() as db:
        session = ReviewSession(
            business_id=str(business.id),
            status="started",
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            updated_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id

    response = client.post(
        f"/api/v1/reviews/session/{session_id}/rating",
        json={"rating": 5},
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Review session has expired"

    with SessionLocal() as db:
        session = db.get(ReviewSession, session_id)
        assert session.status == "expired"


def test_phase_3_10_status_endpoint_reports_expiration():
    business = get_business()
    assert business is not None

    with SessionLocal() as db:
        session = ReviewSession(
            business_id=str(business.id),
            status="started",
            created_at=datetime.now(timezone.utc) - timedelta(hours=2),
            updated_at=datetime.now(timezone.utc) - timedelta(hours=2),
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id

    response = client.get(f"/api/v1/reviews/session/{session_id}/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "expired"
    assert body["expired"] is True


def test_phase_3_11_flow_endpoint_returns_rate_step_for_new_session():
    response = client.post(
        "/api/v1/reviews/session",
        json={"business_slug": "reviewagentai"},
    )
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    flow = client.get(f"/api/v1/reviews/session/{session_id}/flow")
    assert flow.status_code == 200
    body = flow.json()
    assert body["business_slug"] == "reviewagentai"
    assert body["status"] == "started"
    assert body["rating"] is None
    assert body["next_step"] == "rate"
    assert body["expired"] is False


def test_phase_3_11_flow_endpoint_returns_positive_review_step():
    response = client.post(
        "/api/v1/reviews/session",
        json={"business_slug": "reviewagentai"},
    )
    assert response.status_code == 201
    session_id = response.json()["session_id"]

    rating = client.post(
        f"/api/v1/reviews/session/{session_id}/rating",
        json={"rating": 5},
    )
    assert rating.status_code == 200

    flow = client.get(f"/api/v1/reviews/session/{session_id}/flow")
    assert flow.status_code == 200
    body = flow.json()
    assert body["rating"] == 5
    assert body["next_step"] == "positive_review"
