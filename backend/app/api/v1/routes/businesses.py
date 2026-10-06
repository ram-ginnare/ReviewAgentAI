from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.business import BusinessResponse
from backend.app.services.business_service import BusinessService

router = APIRouter(prefix="/businesses", tags=["businesses"])

@router.get("/{slug}", response_model=BusinessResponse)
def get_business(slug: str, db: Session = Depends(get_db)):
    business = BusinessService(db).get_by_slug(slug)
    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    return business
