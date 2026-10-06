from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.access import CustomerAccessRequest, CustomerAccessResponse
from backend.app.services.customer_access_service import CustomerAccessService

router = APIRouter(prefix="/access", tags=["customer-access"])


@router.post(
    "/{slug}",
    response_model=CustomerAccessResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_access(
    slug: str,
    request: CustomerAccessRequest,
    db: Session = Depends(get_db),
):
    try:
        business, review_session, source = (
            CustomerAccessService.create_customer_access(
                db=db,
                slug=slug,
                source=request.source,
            )
        )
    except ValueError as exc:
        message = str(exc)

        if message == "Business not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    return CustomerAccessResponse(
        session_id=review_session.id,
        business_id=str(business.id),
        business_slug=business.slug,
        business_name=business.name,
        source=source,
        status=review_session.status,
        created_at=review_session.created_at,
    )
