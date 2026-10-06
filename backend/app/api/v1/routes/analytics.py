from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.analytics import AnalyticsResponse
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/business/{slug}", response_model=AnalyticsResponse)
def get_business_analytics(
    slug: str,
    days: int | None = Query(default=None, ge=1, le=365),
    db: Session = Depends(get_db),
):
    try:
        return AnalyticsService.get_business_analytics(db=db, slug=slug, days=days)
    except ValueError as exc:
        message = str(exc)
        if message == "Business not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)
