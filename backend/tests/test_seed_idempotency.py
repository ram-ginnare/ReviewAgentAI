from sqlalchemy import select

from backend.app.db.database import SessionLocal
from backend.app.db.seed import seed_demo_data
from backend.app.models.business import Business
from backend.app.models.social_link import SocialLink


def test_demo_seed_is_idempotent_and_removes_obsolete_social_links():
    with SessionLocal() as db:
        business = db.scalar(select(Business).where(Business.slug == "reviewagentai"))
        assert business is not None
        db.add(
            SocialLink(
                business_id=business.id,
                platform="FACEBOOK_TEST",
                url="https://facebook.com/reviewagentai",
                display_order=100,
                enabled=False,
            )
        )
        db.add(
            SocialLink(
                business_id=business.id,
                platform="INSTAGRAM",
                url="https://instagram.com/reviewagentai",
                display_order=99,
                enabled=True,
            )
        )
        db.commit()

    seed_demo_data()
    seed_demo_data()

    with SessionLocal() as db:
        business = db.scalar(select(Business).where(Business.slug == "reviewagentai"))
        links = db.scalars(
            select(SocialLink)
            .where(SocialLink.business_id == business.id)
            .order_by(SocialLink.display_order)
        ).all()

        assert [(link.platform, link.url, link.display_order, link.enabled) for link in links] == [
            ("INSTAGRAM", "https://instagram.com/", 1, True),
            ("FACEBOOK", "https://facebook.com/", 2, True),
            ("YOUTUBE", "https://youtube.com/", 3, True),
            ("WHATSAPP", "https://wa.me/", 4, True),
            ("LINKEDIN", "https://linkedin.com/", 5, True),
        ]
