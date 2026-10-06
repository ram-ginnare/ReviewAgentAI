from fastapi.testclient import TestClient

from backend.app.db.database import SessionLocal
from backend.app.main import app
from backend.app.models.business import Business
from backend.app.models.review_event import ReviewEvent
from backend.app.models.social_link import SocialLink

client = TestClient(app)


def get_business(slug="reviewagentai"):
    with SessionLocal() as db:
        return db.query(Business).filter(Business.slug == slug).first()


def test_business_event_tracking():
    business = get_business()
    assert business is not None

    response = client.post(
        f"/api/v1/events/business/{business.slug}",
        json={
            "event_type": "LANDING_PAGE_VIEW",
            "event_metadata": {"source": "nfc"},
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["business_id"] == business.id
    assert body["event_type"] == "LANDING_PAGE_VIEW"
    assert body["event_metadata"]["source"] == "nfc"


def test_invalid_event_type_is_rejected():
    business = get_business()
    assert business is not None

    response = client.post(
        f"/api/v1/events/business/{business.slug}",
        json={"event_type": "UNKNOWN_EVENT"},
    )

    assert response.status_code == 400
    assert "Unsupported event_type" in response.json()["detail"]


def test_social_link_click_tracking():
    business = get_business()
    assert business is not None

    with SessionLocal() as db:
        link = SocialLink(
            business_id=business.id,
            platform="INSTAGRAM",
            url="https://instagram.com/reviewagentai",
            display_order=99,
            enabled=True,
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        link_id = link.id

    response = client.post(
        f"/api/v1/businesses/{business.slug}/social-links/{link_id}/click"
    )

    assert response.status_code == 201
    body = response.json()
    assert body["business_id"] == business.id
    assert body["social_link_id"] == link_id
    assert body["platform"] == "INSTAGRAM"
    assert body["url"] == "https://instagram.com/reviewagentai"
    assert body["event_id"] > 0

    with SessionLocal() as db:
        event = db.get(ReviewEvent, body["event_id"])
        assert event is not None
        assert event.event_type == "SOCIAL_LINK_CLICKED"
        assert event.event_metadata["social_link_id"] == link_id


def test_disabled_social_link_cannot_be_tracked():
    business = get_business()
    assert business is not None

    with SessionLocal() as db:
        link = SocialLink(
            business_id=business.id,
            platform="FACEBOOK_TEST",
            url="https://facebook.com/reviewagentai",
            display_order=100,
            enabled=False,
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        link_id = link.id

    response = client.post(
        f"/api/v1/businesses/{business.slug}/social-links/{link_id}/click"
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Social link is disabled"
