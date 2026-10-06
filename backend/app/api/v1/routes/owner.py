import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from backend.app.core.security import get_current_user, require_business_owner
from backend.app.db.database import get_db
from backend.app.models.business import Business
from backend.app.models.complaint import LocalComplaint
from backend.app.models.notification import Notification
from backend.app.models.social_link import SocialLink
from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardResponse
from backend.app.schemas.analytics import AnalyticsResponse
from backend.app.schemas.owner_dashboard import OwnerDashboardResponse
from backend.app.schemas.owner_notifications import OwnerNotification, OwnerNotificationList
from backend.app.schemas.business_management import *
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.billing_service import BillingService
from backend.app.services.dashboard_service import DashboardService

router=APIRouter(prefix='/owner',tags=['Business Owner'])

def owner_business(user: User, db: Session):
    if user.role!='BUSINESS_OWNER' or not user.business_id: raise HTTPException(403,'BUSINESS_OWNER_REQUIRED')
    b=db.get(Business,user.business_id)
    if not b: raise HTTPException(404,'Business not found')
    return b

@router.get('/dashboard',response_model=OwnerDashboardResponse)
def dashboard(days:int=Query(30,ge=1,le=365),user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); data=DashboardService.get_business_dashboard(db,b.slug,days); sub=BillingService.subscription(db,b.id)
    unread=int(db.scalar(select(func.count(Notification.id)).where(Notification.business_id==b.id,Notification.status.in_(['PENDING','FAILED']))) or 0)
    return {**data,'plan':sub.plan,'subscription_status':sub.status,'unread_notifications':unread}

@router.get('/notifications',response_model=OwnerNotificationList)
def notifications(status_filter:str|None=Query(None,alias='status',pattern='^(PENDING|PROCESSING|SENT|FAILED)$'),limit:int=Query(50,ge=1,le=100),user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); q=select(Notification).where(Notification.business_id==b.id)
    if status_filter:q=q.where(Notification.status==status_filter)
    items=db.scalars(q.order_by(Notification.created_at.desc()).limit(limit)).all()
    unread=int(db.scalar(select(func.count(Notification.id)).where(Notification.business_id==b.id,Notification.status.in_(['PENDING','FAILED']))) or 0)
    result=[]
    for n in items:
        c=db.get(LocalComplaint,n.complaint_id) if n.complaint_id else None
        result.append(OwnerNotification(id=n.id,complaint_id=n.complaint_id,type=n.type,status=n.status,message=n.message,created_at=n.created_at,sent_at=n.sent_at,complaint_status=c.status if c else None))
    return OwnerNotificationList(items=result,total=int(db.scalar(select(func.count(Notification.id)).where(Notification.business_id==b.id)) or 0),unread=unread)

@router.patch('/complaints/{complaint_id}')
def complaint_status(complaint_id:int,new_status:str=Query(...,pattern='^(NEW|IN_PROGRESS|RESOLVED|CLOSED)$'),user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); c=db.get(LocalComplaint,complaint_id)
    if not c or c.business_id!=b.id: raise HTTPException(404,'Complaint not found')
    c.status=new_status; db.commit(); db.refresh(c); return {'id':c.id,'status':c.status}

@router.get('/settings',response_model=BusinessSettingsResponse)
def settings_get(user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db)
    try: cs=json.loads(b.customer_settings_json or '{}')
    except json.JSONDecodeError: cs={}
    return {**{k:getattr(b,k) for k in ['id','slug','name','description','category','logo_url','welcome_message','brand_primary_color','brand_secondary_color','prefer_ai_comments','google_review_pc_url','google_review_mob_url','nfc_enabled','qr_enabled','updated_at']},'customer_settings':cs}

@router.put('/settings/profile',response_model=BusinessSettingsResponse)
def profile(payload:BusinessProfileUpdate,user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); [setattr(b,k,getattr(payload,k)) for k in ['name','description','category','logo_url','welcome_message']]; db.commit(); db.refresh(b); return settings_get(user,db)

@router.put('/settings/branding',response_model=BusinessSettingsResponse)
def branding(payload:BrandingUpdate,user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); b.brand_primary_color=payload.brand_primary_color; b.brand_secondary_color=payload.brand_secondary_color; db.commit(); db.refresh(b); return settings_get(user,db)

@router.put('/settings/reviews',response_model=BusinessSettingsResponse)
def review_settings(payload:ReviewSettingsUpdate,user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); b.prefer_ai_comments=payload.prefer_ai_comments; b.google_review_pc_url=payload.google_review_pc_url; b.google_review_mob_url=payload.google_review_mob_url; b.nfc_enabled=payload.nfc_enabled; b.qr_enabled=payload.qr_enabled; b.customer_settings_json=json.dumps(payload.customer_settings); db.commit(); db.refresh(b); return settings_get(user,db)

@router.get('/social-links')
def social_get(user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); return db.scalars(select(SocialLink).where(SocialLink.business_id==b.id).order_by(SocialLink.display_order,SocialLink.id)).all()

@router.post('/social-links',status_code=201)
def social_create(payload:SocialLinkCreate,user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); row=SocialLink(business_id=b.id,**payload.model_dump()); db.add(row); db.commit(); db.refresh(row); return row

@router.put('/social-links/{link_id}')
def social_update(link_id:int,payload:SocialLinkUpdate,user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); row=db.get(SocialLink,link_id)
    if not row or row.business_id!=b.id: raise HTTPException(404,'Social link not found')
    for k,v in payload.model_dump().items(): setattr(row,k,v)
    db.commit(); db.refresh(row); return row

@router.delete('/social-links/{link_id}',status_code=204)
def social_delete(link_id:int,user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    b=owner_business(user,db); row=db.get(SocialLink,link_id)
    if not row or row.business_id!=b.id: raise HTTPException(404,'Social link not found')
    db.delete(row); db.commit()
