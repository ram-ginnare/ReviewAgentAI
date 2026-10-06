from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.business import Business

class BusinessService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_slug(self, slug: str) -> Business | None:
        statement = (
            select(Business)
            .options(selectinload(Business.social_links))
            .where(
                Business.slug == slug,
                Business.status == "ACTIVE",
            )
        )
        return self.db.scalar(statement)
