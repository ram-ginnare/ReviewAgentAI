from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.review_event import SocialLinkClickResponse
from backend.app.services.review_event_service import ReviewEventService

router = APIRouter(prefix="/businesses", tags=["Social Links"])


@router.post(
    "/{slug}/social-links/{social_link_id}/click",
    response_model=SocialLinkClickResponse,
    status_code=status.HTTP_201_CREATED,
)
def track_social_link_click(
    slug: str,
    social_link_id: int,
    db: Session = Depends(get_db),
):
    try:
        social_link, event = ReviewEventService.record_social_link_click(
            db=db,
            slug=slug,
            social_link_id=social_link_id,
        )
    except ValueError as exc:
        message = str(exc)
        if message == "Business not found" or message == "Social link not found":
            raise HTTPException(status_code=404, detail=message)
        raise HTTPException(status_code=409, detail=message)

    return SocialLinkClickResponse(
        business_id=event.business_id,
        social_link_id=social_link.id,
        platform=social_link.platform,
        url=social_link.url,
        event_id=event.id,
    )
