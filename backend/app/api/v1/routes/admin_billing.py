from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import require_admin
from backend.app.db.database import get_db
from backend.app.models.business import Business
from backend.app.models.subscription import Subscription
from backend.app.models.subscription_plan import SubscriptionPlan
from backend.app.models.user import User
from backend.app.schemas.admin_billing import (
    AdminPlanResponse,
    AdminPlanUpdateRequest,
    AdminSubscriptionItem,
    AdminSubscriptionUpdateRequest,
)
from backend.app.services.billing_service import BillingService

router = APIRouter(prefix='/admin/billing', tags=['Admin Billing'])


@router.get('/plans', response_model=list[AdminPlanResponse])
def list_plans(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    BillingService.ensure_plans(db)
    return db.scalars(select(SubscriptionPlan).order_by(SubscriptionPlan.id)).all()


@router.put('/plans/{code}', response_model=AdminPlanResponse)
def update_plan(code: str, payload: AdminPlanUpdateRequest, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == code.upper()))
    if plan is None:
        raise HTTPException(404, 'Subscription plan not found')
    if not payload.is_active and db.scalar(select(Subscription).where(Subscription.plan == plan.code, Subscription.status.in_(['ACTIVE', 'TRIALING', 'PAST_DUE']))) is not None:
        raise HTTPException(409, 'Cannot deactivate a plan that is currently assigned to an active subscription')
    plan.name = payload.name.strip()
    plan.price_paise = payload.price_paise
    plan.monthly_review_limit = payload.monthly_review_limit
    plan.trial_days = payload.trial_days
    plan.is_active = payload.is_active
    db.commit()
    db.refresh(plan)
    return plan


@router.get('/subscriptions', response_model=list[AdminSubscriptionItem])
def list_subscriptions(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    BillingService.ensure_plans(db)
    businesses = db.scalars(select(Business).order_by(Business.name)).all()
    result = []
    for business in businesses:
        sub = BillingService.subscription(db, business.id)
        plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == sub.plan))
        owner = db.scalar(select(User).where(User.business_id == business.id, User.role == 'BUSINESS_OWNER', User.is_active.is_(True)).order_by(User.id))
        result.append(AdminSubscriptionItem(
            business_id=business.id,
            business_name=business.name,
            business_slug=business.slug,
            owner_email=owner.email if owner else None,
            plan=sub.plan,
            plan_name=plan.name if plan else sub.plan.title(),
            status=sub.status,
            provider=sub.provider,
            trial_ends_at=sub.trial_ends_at,
            current_period_start=sub.current_period_start,
            current_period_end=sub.current_period_end,
            cancel_at_period_end=sub.cancel_at_period_end,
            plan_price_paise=plan.price_paise if plan else 0,
            monthly_review_limit=plan.monthly_review_limit if plan else 0,
        ))
    return result


@router.put('/subscriptions/{business_id}', response_model=AdminSubscriptionItem)
def update_subscription(business_id: int, payload: AdminSubscriptionUpdateRequest, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    business = db.get(Business, business_id)
    if business is None:
        raise HTTPException(404, 'Business not found')
    plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == payload.plan.upper(), SubscriptionPlan.is_active.is_(True)))
    if plan is None:
        raise HTTPException(422, 'Selected subscription plan is not active or does not exist')
    if payload.current_period_end and payload.current_period_start and payload.current_period_end < payload.current_period_start:
        raise HTTPException(422, 'Current period end cannot be before current period start')
    sub = BillingService.subscription(db, business_id)
    sub.plan = plan.code
    sub.status = payload.status
    sub.trial_ends_at = payload.trial_ends_at
    sub.current_period_start = payload.current_period_start
    sub.current_period_end = payload.current_period_end
    sub.cancel_at_period_end = payload.cancel_at_period_end
    db.commit()
    db.refresh(sub)
    owner = db.scalar(select(User).where(User.business_id == business.id, User.role == 'BUSINESS_OWNER', User.is_active.is_(True)).order_by(User.id))
    return AdminSubscriptionItem(
        business_id=business.id,
        business_name=business.name,
        business_slug=business.slug,
        owner_email=owner.email if owner else None,
        plan=sub.plan,
        plan_name=plan.name,
        status=sub.status,
        provider=sub.provider,
        trial_ends_at=sub.trial_ends_at,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=sub.cancel_at_period_end,
        plan_price_paise=plan.price_paise,
        monthly_review_limit=plan.monthly_review_limit,
    )
