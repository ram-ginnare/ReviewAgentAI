import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.core.security import require_admin
from backend.app.db.database import get_db
from backend.app.models.business import Business
from backend.app.models.complaint import LocalComplaint
from backend.app.models.generated_review import GeneratedPositiveReview
from backend.app.models.social_link import SocialLink
from backend.app.models.subscription_plan import SubscriptionPlan
from backend.app.models.user import User
from backend.app.schemas.admin_business import (
    AdminBusinessCreate, AdminBusinessItem, AdminBusinessListResponse,
    AdminBusinessUpdate, AdminOwnerOption, AdminSocialLink,
)
from backend.app.services.billing_service import BillingService

router = APIRouter(prefix='/admin/businesses', tags=['Admin Businesses'])


def _customer_settings(b: Business) -> dict:
    if not b.customer_settings_json:
        return {}
    try:
        value = json.loads(b.customer_settings_json)
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError):
        return {}


def _owner(db: Session, business_id: int):
    return db.scalar(select(User).where(User.business_id == business_id, User.role == 'BUSINESS_OWNER').order_by(User.id))


def _item(db: Session, b: Business) -> AdminBusinessItem:
    owner = _owner(db, b.id)
    sub = BillingService.subscription(db, b.id)
    plan = db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == sub.plan))
    reviews = int(db.scalar(select(func.count(GeneratedPositiveReview.id)).where(GeneratedPositiveReview.business_id == b.id)) or 0)
    complaints = int(db.scalar(select(func.count(LocalComplaint.id)).where(LocalComplaint.business_id == b.id)) or 0)
    avg = db.scalar(select(func.avg(GeneratedPositiveReview.rating)).where(GeneratedPositiveReview.business_id == b.id))
    return AdminBusinessItem(
        id=b.id, slug=b.slug, name=b.name, description=b.description, category=b.category,
        logo_url=b.logo_url, google_review_pc_url=b.google_review_pc_url,
        google_review_mob_url=b.google_review_mob_url, status=b.status,
        prefer_ai_comments=b.prefer_ai_comments, brand_primary_color=b.brand_primary_color,
        brand_secondary_color=b.brand_secondary_color, welcome_message=b.welcome_message,
        nfc_enabled=b.nfc_enabled, qr_enabled=b.qr_enabled, customer_settings=_customer_settings(b),
        owner_id=owner.id if owner else None, owner_email=owner.email if owner else None,
        owner_name=owner.full_name if owner else None, plan=sub.plan,
        plan_name=plan.name if plan else sub.plan.title(), subscription_status=sub.status,
        review_count=reviews, complaint_count=complaints,
        average_rating=round(float(avg), 2) if avg is not None else None,
        social_links=[AdminSocialLink(id=s.id, platform=s.platform, url=s.url, display_order=s.display_order, enabled=s.enabled) for s in b.social_links],
        created_at=b.created_at, updated_at=b.updated_at,
    )


def _validate_owner(db: Session, owner_id: int | None, business_id: int | None = None):
    if owner_id is None:
        return None
    owner = db.get(User, owner_id)
    if owner is None or owner.role != 'BUSINESS_OWNER' or not owner.is_active:
        raise HTTPException(422, 'Selected owner is not an active business owner')
    if owner.business_id is not None and owner.business_id != business_id:
        raise HTTPException(409, 'Selected owner is already assigned to another business')
    return owner


def _apply(b: Business, p: AdminBusinessCreate):
    b.slug=p.slug.strip(); b.name=p.name.strip(); b.description=p.description; b.category=p.category; b.logo_url=p.logo_url
    b.google_review_pc_url=p.google_review_pc_url; b.google_review_mob_url=p.google_review_mob_url; b.status=p.status
    b.prefer_ai_comments=p.prefer_ai_comments; b.brand_primary_color=p.brand_primary_color; b.brand_secondary_color=p.brand_secondary_color
    b.welcome_message=p.welcome_message; b.nfc_enabled=p.nfc_enabled; b.qr_enabled=p.qr_enabled
    b.customer_settings_json=json.dumps(p.customer_settings, separators=(',', ':'))


def _replace_social(db: Session, b: Business, links: list[AdminSocialLink]):
    for old in list(b.social_links):
        db.delete(old)
    db.flush()
    for link in links:
        db.add(SocialLink(business_id=b.id, platform=link.platform.strip(), url=link.url.strip(), display_order=link.display_order, enabled=link.enabled))


@router.get('', response_model=AdminBusinessListResponse)
def list_businesses(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    businesses = db.scalars(select(Business).options(selectinload(Business.social_links)).order_by(Business.name)).all()
    owners = db.scalars(select(User).where(User.role == 'BUSINESS_OWNER').order_by(User.full_name, User.email)).all()
    return AdminBusinessListResponse(
        businesses=[_item(db, b) for b in businesses],
        owners=[AdminOwnerOption(id=o.id, email=o.email, full_name=o.full_name, business_id=o.business_id, is_active=o.is_active) for o in owners],
    )


@router.get('/{business_id}', response_model=AdminBusinessItem)
def get_business(business_id: int, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    b=db.scalar(select(Business).options(selectinload(Business.social_links)).where(Business.id == business_id))
    if b is None: raise HTTPException(404, 'Business not found')
    return _item(db,b)


@router.post('', response_model=AdminBusinessItem, status_code=status.HTTP_201_CREATED)
def create_business(payload: AdminBusinessCreate, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    if db.scalar(select(Business).where(Business.slug == payload.slug.strip())) is not None:
        raise HTTPException(409, 'Business slug already exists')
    owner=_validate_owner(db,payload.owner_id)
    b=Business(slug=payload.slug.strip(), name=payload.name.strip(), google_review_pc_url=payload.google_review_pc_url, google_review_mob_url=payload.google_review_mob_url)
    _apply(b,payload); db.add(b); db.flush(); _replace_social(db,b,payload.social_links)
    if owner: owner.business_id=b.id
    BillingService.subscription(db,b.id)
    db.commit(); db.refresh(b)
    return _item(db,b)


@router.put('/{business_id}', response_model=AdminBusinessItem)
def update_business(business_id: int, payload: AdminBusinessUpdate, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    b=db.scalar(select(Business).options(selectinload(Business.social_links)).where(Business.id == business_id))
    if b is None: raise HTTPException(404, 'Business not found')
    duplicate=db.scalar(select(Business).where(Business.slug == payload.slug.strip(), Business.id != business_id))
    if duplicate is not None: raise HTTPException(409, 'Business slug already exists')
    owner=_validate_owner(db,payload.owner_id,business_id)
    old_owner=_owner(db,business_id)
    if old_owner and old_owner.id != payload.owner_id: old_owner.business_id=None
    _apply(b,payload); _replace_social(db,b,payload.social_links)
    if owner: owner.business_id=b.id
    db.commit(); db.refresh(b)
    return _item(db,b)


@router.patch('/{business_id}/status', response_model=AdminBusinessItem)
def toggle_business(business_id: int, active: bool, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    b=db.get(Business,business_id)
    if b is None: raise HTTPException(404, 'Business not found')
    b.status='ACTIVE' if active else 'INACTIVE'; db.commit(); db.refresh(b)
    return _item(db,b)
