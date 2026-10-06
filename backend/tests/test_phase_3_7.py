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


def test_nfc_customer_access_creates_session_and_event():
    business = get_business()
    assert business is not None

    response = client.post(
        f"/api/v1/access/{business.slug}",
        json={"source": "nfc"},
    )

    assert response.status_code == 201
    body = response.json()

    assert body["business_id"] == str(business.id)
    assert body["business_slug"] == business.slug
    assert body["source"] == "nfc"
    assert body["status"] == "started"
    assert body["session_id"]

    with SessionLocal() as db:
        session = db.get(ReviewSession, body["session_id"])
        assert session is not None
        assert session.business_id == str(business.id)

        event = (
            db.query(ReviewEvent)
            .filter(
                ReviewEvent.business_id == business.id,
                ReviewEvent.event_type == "LANDING_PAGE_VIEW",
            )
            .order_by(ReviewEvent.id.desc())
            .first()
        )
        assert event is not None
        assert event.event_metadata["source"] == "nfc"
        assert event.event_metadata["session_id"] == body["session_id"]


def test_qr_customer_access_is_supported():
    business = get_business()
    assert business is not None

    response = client.post(
        f"/api/v1/access/{business.slug}",
        json={"source": "qr"},
    )

    assert response.status_code == 201
    assert response.json()["source"] == "qr"


def test_invalid_customer_access_source_is_rejected():
    business = get_business()
    assert business is not None

    response = client.post(
        f"/api/v1/access/{business.slug}",
        json={"source": "email"},
    )

    assert response.status_code == 409
    assert "Unsupported source" in response.json()["detail"]


def test_unknown_business_access_is_rejected():
    response = client.post(
        "/api/v1/access/does-not-exist",
        json={"source": "nfc"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Business not found"
