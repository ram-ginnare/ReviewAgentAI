from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from backend.app.models.subscription_plan import SubscriptionPlan
from sqlalchemy.orm import Session
from backend.app.core.security import require_business_owner
from backend.app.db.database import get_db
from backend.app.models.user import User
from backend.app.models.subscription import BillingPayment
from backend.app.schemas.billing import *
from backend.app.services.billing_service import BillingService
router=APIRouter(prefix='/billing',tags=['Billing'])
@router.get('/plans',response_model=list[PlanResponse])
def plans(db: Session = Depends(get_db)):
    BillingService.ensure_plans(db)
    return [PlanResponse(code=p.code,name=p.name,price_paise=p.price_paise,monthly_review_limit=p.monthly_review_limit) for p in db.scalars(select(SubscriptionPlan).where(SubscriptionPlan.is_active.is_(True)).order_by(SubscriptionPlan.id)).all()]
@router.get('/subscription',response_model=SubscriptionResponse)
def subscription(user:User=Depends(require_business_owner),db:Session=Depends(get_db)): return BillingService.subscription(db,user.business_id)
@router.post('/checkout',response_model=CheckoutResponse)
def checkout(payload:dict,user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    try: payment,order=BillingService.checkout(db,user.business_id,payload.get('plan',''))
    except ValueError as e: raise HTTPException(422,str(e))
    return CheckoutResponse(payment_id=payment.id,provider=payment.provider,provider_order_id=order,amount_paise=payment.amount_paise,currency=payment.currency,receipt_reference=payment.receipt_reference,status=payment.status)
@router.post('/confirm',response_model=CheckoutResponse)
def confirm(payload:PaymentConfirmRequest,user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    payment=db.get(BillingPayment,payload.payment_id)
    if not payment or payment.business_id!=user.business_id: raise HTTPException(404,'Payment not found')
    payment=BillingService.confirm(db,payment.id,payload.success)
    return CheckoutResponse(payment_id=payment.id,provider=payment.provider,provider_order_id=f'mock_order_{payment.id}',amount_paise=payment.amount_paise,currency=payment.currency,receipt_reference=payment.receipt_reference,status=payment.status)
@router.post('/cancel')
def cancel(user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    sub=BillingService.subscription(db,user.business_id); sub.cancel_at_period_end=True; db.commit(); return {'status':sub.status,'cancel_at_period_end':True}
@router.get('/history',response_model=list[BillingHistoryItem])
def history(user:User=Depends(require_business_owner),db:Session=Depends(get_db)):
    return db.scalars(select(BillingPayment).where(BillingPayment.business_id==user.business_id).order_by(BillingPayment.created_at.desc())).all()
