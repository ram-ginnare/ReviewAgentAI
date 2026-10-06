from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from backend.app.db.base import Base
from backend.app.models import Business, SocialLink, LocalComplaint, FallbackReviewComment

def test_all_phase1_tables_are_created():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    tables = set(inspect(engine).get_table_names())
    assert {
        "businesses",
        "social_links",
        "local_complaints",
        "generated_positive_reviews",
        "review_events",
        "notifications",
        "review_sessions",
        "fallback_review_comments",
    }.issubset(tables)

def test_business_to_social_link_relationship():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        business = Business(
            slug="test-business",
            name="Test Business",
            description="Test",
            category="Restaurant",
            google_review_pc_url="https://example.com/google-review",
            google_review_mob_url="https://example.com/google-review-mobile",
        )
        business.social_links.append(
            SocialLink(
                platform="INSTAGRAM",
                url="https://instagram.com/test",
                display_order=1,
            )
        )
        db.add(business)
        db.commit()

        loaded = db.query(Business).filter_by(slug="test-business").one()
        assert len(loaded.social_links) == 1
        assert loaded.social_links[0].platform == "INSTAGRAM"

def test_database_can_store_complaint():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        business = Business(
            slug="complaint-business",
            name="Complaint Business",
            google_review_pc_url="https://example.com/google-review",
            google_review_mob_url="https://example.com/google-review-mobile",
        )
        db.add(business)
        db.flush()

        complaint = LocalComplaint(
            business_id=business.id,
            rating=2,
            comments="Service needs improvement.",
        )
        db.add(complaint)
        db.commit()

        assert complaint.id is not None
        assert complaint.rating == 2
