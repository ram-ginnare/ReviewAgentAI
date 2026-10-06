from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.review_event import ReviewEventCreate, ReviewEventResponse
from backend.app.services.review_event_service import ReviewEventService

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "/business/{slug}",
    response_model=ReviewEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_business_event(
    slug: str,
    request: ReviewEventCreate,
    db: Session = Depends(get_db),
):
    try:
        event = ReviewEventService.record_business_event(
            db=db,
            slug=slug,
            event_type=request.event_type,
            rating=request.rating,
            event_metadata=request.event_metadata,
        )
    except ValueError as exc:
        message = str(exc)
        if message == "Business not found":
            raise HTTPException(status_code=404, detail=message)
        if message == "Business is not active":
            raise HTTPException(status_code=409, detail=message)
        raise HTTPException(status_code=400, detail=message)

    return event
