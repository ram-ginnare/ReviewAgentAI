from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.core.rate_limit import InMemoryRateLimiter
from backend.app.core.config import settings
from backend.app.core.statuses import ReviewSessionStatus
from backend.app.core.errors import api_error

from backend.app.schemas.review_session import (
    ReviewSessionCreate,
    ReviewSessionResponse,
)
from backend.app.services.review_session_service import (
    ReviewSessionService,
)

from backend.app.schemas.review_rating import (
    ReviewRatingRequest,
    ReviewRatingResponse,
)

from backend.app.schemas.generated_review import (
    GeneratedReviewItem,
    PositiveReviewRequest,
    PositiveReviewResponse,
)

from backend.app.services.generated_review_service import (
    GeneratedReviewService,
)
from backend.app.schemas.google_review import (
    GoogleReviewSelectionResponse,
    SelectReviewRequest,
)
from backend.app.services.google_review_service import GoogleReviewService
from backend.app.schemas.private_feedback import (
    PrivateFeedbackRequest,
    PrivateFeedbackResponse,
)
from backend.app.services.private_feedback_service import PrivateFeedbackService
from backend.app.services.billing_service import BillingService
from backend.app.schemas.review_session_flow import ReviewSessionStatusResponse, ReviewFlowResponse

ai_rate_limiter = InMemoryRateLimiter(
    max_requests=settings.ai_rate_limit_requests,
    window_seconds=settings.ai_rate_limit_window_seconds,
)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


@router.post(
    "/session",
    response_model=ReviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review_session(
    request: ReviewSessionCreate,
    db: Session = Depends(get_db),
):
    try:
        review_session = ReviewSessionService.create_session(
            db=db,
            business_slug=request.business_slug,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return ReviewSessionResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        business_slug=request.business_slug,
        status=review_session.status,
        created_at=review_session.created_at,
    )


@router.post(
    "/session/{session_id}/rating",
    response_model=ReviewRatingResponse,
)
def rate_review_session(
    session_id: str,
    request: ReviewRatingRequest,
    db: Session = Depends(get_db),
):
    try:
        review_session = ReviewSessionService.rate_session(
            db=db,
            session_id=session_id,
            rating=request.rating,
        )
    except ValueError as exc:
        message = str(exc)

        if message == "Review session not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    if request.rating >= 4:
        next_step = ReviewSessionStatus.POSITIVE_REVIEW
    else:
        next_step = ReviewSessionStatus.PRIVATE_FEEDBACK

    return ReviewRatingResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        rating=review_session.rating,
        status=review_session.status,
        next_step=next_step,
        updated_at=review_session.updated_at,
    )


@router.post(
    "/session/{session_id}/positive-reviews",
    response_model=PositiveReviewResponse,
)
def generate_positive_reviews(
    session_id: str,
    request: PositiveReviewRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    client_host = http_request.client.host if http_request.client else "unknown"
    rate_key = client_host
    if not ai_rate_limiter.allow(rate_key):
        raise api_error(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "Too many AI review generation requests. Please try again shortly.",
            "AI_RATE_LIMITED",
            {"Retry-After": str(settings.ai_rate_limit_window_seconds)},
        )

    try:
        from backend.app.models.review_session import ReviewSession
        session_obj = db.get(ReviewSession, session_id)
        if session_obj is not None and not BillingService.within_usage_limit(db, session_obj.business_id):
            raise HTTPException(status_code=402, detail="Monthly review limit reached for the current plan", headers={"X-Error-Code":"PLAN_LIMIT_REACHED"})
        review_session, reviews, generation_result, review_input = (
            GeneratedReviewService.generate_positive_reviews(
                db=db,
                session_id=session_id,
                professional_staff=request.professional_staff,
                reliable_service=request.reliable_service,
                good_ambiance=request.good_ambiance,
                affordable_pricing=request.affordable_pricing,
                customer_comment=request.customer_comment,
            )
        )
        generation_source = generation_result.source

    except ValueError as exc:
        message = str(exc)

        if message == "Review session not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        if message == "Groq API key is not configured":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=message,
            )

        if message.startswith("Groq"):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )

    return PositiveReviewResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        rating=review_session.rating,
        generation_source=generation_source,
        selected_preferences=review_input.selected_preferences,
        customer_comment=review_input.customer_comment or None,
        reviews=[
            GeneratedReviewItem(
                id=review.id,
                generated_review=review.generated_review,
                selected=review.selected,
                created_at=review.created_at,
            )
            for review in reviews
        ],
    )


@router.post(
    "/session/{session_id}/private-feedback",
    response_model=PrivateFeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_private_feedback(
    session_id: str,
    request: PrivateFeedbackRequest,
    db: Session = Depends(get_db),
):
    try:
        review_session, complaint, acknowledgement = (
            PrivateFeedbackService.submit_feedback(
                db=db,
                session_id=session_id,
                comments=request.comments,
            )
        )
    except ValueError as exc:
        message = str(exc)
        if message == "Review session not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    return PrivateFeedbackResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        complaint_id=complaint.id,
        rating=review_session.rating,
        status=review_session.status,
        acknowledgement=acknowledgement,
        created_at=complaint.created_at,
    )


@router.post(
    "/session/{session_id}/google-review/select",
    response_model=GoogleReviewSelectionResponse,
)
def select_google_review(
    session_id: str,
    request: SelectReviewRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    try:
        review_session, review, business = GoogleReviewService.select_review(
            db=db,
            session_id=session_id,
            review_id=request.review_id,
            final_review_text=request.final_review_text,
        )
    except ValueError as exc:
        message = str(exc)

        if message in {"Review session not found", "Generated review not found", "Business not found"}:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=message,
            )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=message,
        )

    review_url, device_type = GoogleReviewService.get_review_url(
        business, http_request.headers.get("user-agent")
    )

    return GoogleReviewSelectionResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        rating=review_session.rating,
        selected_review_id=review.id,
        review_text=review.generated_review,
        google_review_pc_url=business.google_review_pc_url,
        google_review_mob_url=business.google_review_mob_url,
        google_review_url=review_url,
        device_type=device_type,
        status=review_session.status,
        updated_at=review_session.updated_at,
    )


@router.get("/session/{session_id}/status", response_model=ReviewSessionStatusResponse)
def get_review_session_status(
    session_id: str,
    db: Session = Depends(get_db),
):
    try:
        review_session = ReviewSessionService.get_session(db, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    expired = ReviewSessionService.is_expired(review_session)
    if expired and review_session.status != ReviewSessionStatus.EXPIRED and review_session.status not in {ReviewSessionStatus.COMPLETED}:
        review_session.status = ReviewSessionStatus.EXPIRED
        db.commit()
        db.refresh(review_session)

    return ReviewSessionStatusResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        status=review_session.status,
        rating=review_session.rating,
        expires_at=ReviewSessionService.expires_at(review_session),
        expired=review_session.status == ReviewSessionStatus.EXPIRED,
    )


@router.get("/session/{session_id}/flow", response_model=ReviewFlowResponse)
def get_review_flow(
    session_id: str,
    db: Session = Depends(get_db),
):
    try:
        review_session = ReviewSessionService.get_session(db, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    expired = ReviewSessionService.is_expired(review_session)
    if expired and review_session.status not in {ReviewSessionStatus.COMPLETED, ReviewSessionStatus.EXPIRED}:
        review_session.status = ReviewSessionStatus.EXPIRED
        db.commit()
        db.refresh(review_session)

    try:
        from backend.app.models.business import Business
        business = db.get(Business, int(review_session.business_id))
        if business is None:
            raise ValueError("Business not found")
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    if review_session.status == ReviewSessionStatus.EXPIRED:
        next_step = ReviewSessionStatus.EXPIRED
    elif review_session.status == ReviewSessionStatus.COMPLETED:
        next_step = ReviewSessionStatus.COMPLETED
    elif review_session.rating is None:
        next_step = ReviewSessionStatus.RATE
    elif review_session.rating >= 4:
        next_step = ReviewSessionStatus.POSITIVE_REVIEW
    else:
        next_step = ReviewSessionStatus.PRIVATE_FEEDBACK

    return ReviewFlowResponse(
        session_id=review_session.id,
        business_id=review_session.business_id,
        business_slug=business.slug,
        business_name=business.name,
        status=review_session.status,
        rating=review_session.rating,
        next_step=next_step,
        expires_at=ReviewSessionService.expires_at(review_session),
        expired=review_session.status == ReviewSessionStatus.EXPIRED,
    )
