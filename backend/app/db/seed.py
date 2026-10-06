from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from backend.app.db.database import SessionLocal
from backend.app.models.business import Business
from backend.app.models.fallback_review_comment import FallbackReviewComment
from backend.app.models.social_link import SocialLink
from backend.app.models.user import User
from backend.app.core.security import hash_password
from backend.app.core.config import settings
from backend.app.models.subscription import Subscription
from backend.app.models.subscription_plan import SubscriptionPlan

REVIEWAGENTAI_BUSINESS = {
    "slug": "reviewagentai",
    "name": "Review Agent AI",
    "logo_url": "/logos/reviewagentai.jpg",
    "description": "Review Agent AI is an AI-powered platform that helps businesses generate authentic customer reviews and feedback. Our advanced AI algorithms analyze customer interactions and provide valuable insights to improve your business reputation and customer satisfaction.",
    "category": "AI & Technology",
    "google_review_pc_url": "https://search.google.com/local/writereview?placeid=ChIJV0S728r9YjkRBfIuWZfvmZ8",
    "google_review_mob_url": "https://g.page/r/CQXyLImX75mfEBM/review",
    "status": "ACTIVE",
    "prefer_ai_comments": True,
}

LEGACY_DEMO_BUSINESS = {
    "slug": "abc-restaurant",
    "name": "ABC Restaurant",
    "logo_url": "",
    "description": "Great food. Great service. Always here for you.",
    "category": "Restaurant",
    "google_review_pc_url": "https://search.google.com/local/writereview?placeid=REPLACE_ME",
    "google_review_mob_url": "https://g.page/r/CQXyLImX75mfEBM/review",
    "status": "ACTIVE",
    "prefer_ai_comments": False,
}

DEMO_LINKS = [
    ("INSTAGRAM", "https://instagram.com/", 1),
    ("FACEBOOK", "https://facebook.com/", 2),
    ("YOUTUBE", "https://youtube.com/", 3),
    ("WHATSAPP", "https://wa.me/", 4),
    ("LINKEDIN", "https://linkedin.com/", 5),
]

# Database-managed complete fallback review comments.
# These comments intentionally contain no runtime placeholders.
DEFAULT_FALLBACK_COMMENTS = {
    4: [
        "Good overall experience with professional staff and reliable service. The atmosphere was pleasant and the pricing was reasonable.",
        "A positive experience with helpful staff, dependable service, and a comfortable ambiance. I would be happy to visit again.",
        "Really enjoyed the visit. The team was courteous, the service was smooth, and the overall atmosphere was welcoming.",
    ],
    5: [
        "Excellent experience with professional and friendly staff. The service was reliable, the ambiance was pleasant, and the pricing felt reasonable. I would definitely recommend this place.",
        "Really enjoyed my visit. The staff were professional, the service was dependable, and the overall atmosphere was welcoming. Great value for the experience.",
        "A wonderful experience overall. Everything was handled professionally, the service was smooth, and the ambiance made the visit enjoyable. I would happily come back again.",
    ],
}



DEFAULT_PLANS = [
    ("STARTER", "Starter", 99900, 100, 14),
    ("PROFESSIONAL", "Professional", 249900, 500, 14),
    ("BUSINESS", "Business", 499900, 2000, 14),
]


def _seed_plans(db) -> None:
    for code, name, price_paise, monthly_review_limit, trial_days in DEFAULT_PLANS:
        plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == code))
        if plan is None:
            db.add(SubscriptionPlan(code=code, name=name, price_paise=price_paise, monthly_review_limit=monthly_review_limit, trial_days=trial_days, is_active=True))
        else:
            # Keep admin-customized price/limit/name intact; only repair missing/invalid values.
            if plan.trial_days < 0:
                plan.trial_days = trial_days

def _seed_social_links(db, business: Business) -> None:
    canonical_platforms = {platform for platform, _, _ in DEMO_LINKS}
    existing_links = db.scalars(
        select(SocialLink)
        .where(SocialLink.business_id == business.id)
        .order_by(SocialLink.id)
    ).all()

    first_by_platform: dict[str, SocialLink] = {}
    for link in existing_links:
        if link.platform not in canonical_platforms or link.platform in first_by_platform:
            db.delete(link)
            continue
        first_by_platform[link.platform] = link

    for platform, url, display_order in DEMO_LINKS:
        link = first_by_platform.get(platform)
        if link is None:
            db.add(
                SocialLink(
                    business_id=business.id,
                    platform=platform,
                    url=url,
                    display_order=display_order,
                    enabled=True,
                )
            )
        else:
            link.url = url
            link.display_order = display_order
            link.enabled = True


def _seed_fallback_comments(db, business: Business) -> None:
    for rating, comments in DEFAULT_FALLBACK_COMMENTS.items():
        existing = db.scalars(
            select(FallbackReviewComment)
            .where(
                FallbackReviewComment.business_id == business.id,
                FallbackReviewComment.rating == rating,
            )
            .order_by(FallbackReviewComment.id)
        ).all()

        first_by_order: dict[int, FallbackReviewComment] = {}
        for row in existing:
            if row.display_order in first_by_order:
                db.delete(row)
                continue
            first_by_order[row.display_order] = row

        for display_order, comment in enumerate(comments, start=1):
            row = first_by_order.get(display_order)
            if row is None:
                db.add(
                    FallbackReviewComment(
                        business_id=business.id,
                        rating=rating,
                        comment=comment,
                        display_order=display_order,
                        enabled=True,
                    )
                )
            else:
                row.comment = comment
                row.enabled = True

        # Remove extra old/test fallback comments.
        for display_order, row in first_by_order.items():
            if display_order > len(comments):
                db.delete(row)


def _seed_business(db, business_data: dict) -> None:
    business = db.scalar(select(Business).where(Business.slug == business_data["slug"]))

    if business is None:
        business = Business(**business_data)
        db.add(business)
        db.flush()
    else:
        for field, value in business_data.items():
            if getattr(business, field) != value:
                setattr(business, field, value)

    _seed_social_links(db, business)
    _seed_fallback_comments(db, business)
    if db.scalar(select(Subscription).where(Subscription.business_id == business.id)) is None:
        db.add(Subscription(business_id=business.id, plan="STARTER", status="TRIALING", provider="MOCK", trial_ends_at=datetime.now(timezone.utc).replace(tzinfo=None)+timedelta(days=14)))



def _seed_users(db) -> None:
    users = [
        {
            "email": "admin@reviewagentai.local",
            "password": "Admin@12345",
            "full_name": "ReviewAgentAI Admin",
            "role": "ADMIN",
            "business_slug": None,
        },
        {
            "email": "owner@reviewagentai.local",
            "password": "Owner@12345",
            "full_name": "ReviewAgentAI Business Owner",
            "role": "BUSINESS_OWNER",
            "business_slug": "reviewagentai",
        },
    ]
    for item in users:
        user = db.scalar(select(User).where(User.email == item["email"]))
        business = db.scalar(select(Business).where(Business.slug == item["business_slug"])) if item["business_slug"] else None
        if user is None:
            db.add(User(email=item["email"], password_hash=hash_password(item["password"]), full_name=item["full_name"], role=item["role"], business_id=business.id if business else None, is_active=True))
        else:
            user.full_name = item["full_name"]
            user.role = item["role"]
            user.business_id = business.id if business else None
            user.is_active = True


def seed_demo_data() -> None:
    with SessionLocal() as db:
        _seed_plans(db)
        _seed_business(db, REVIEWAGENTAI_BUSINESS)
        _seed_business(db, LEGACY_DEMO_BUSINESS)
        if settings.demo_auth_seed:
            _seed_users(db)
        db.commit()
