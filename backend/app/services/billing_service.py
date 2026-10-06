from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy import select, func
from backend.app.models.generated_review import GeneratedPositiveReview
from sqlalchemy.orm import Session
from backend.app.models.business import Business
from backend.app.models.subscription import Subscription, BillingPayment
from backend.app.models.subscription_plan import SubscriptionPlan
from backend.app.schemas.billing import PLANS

class BillingService:
    @staticmethod
    def ensure_plans(db: Session) -> None:
        defaults = [
            ("STARTER", "Starter", 99900, 100, 14),
            ("PROFESSIONAL", "Professional", 249900, 500, 14),
            ("BUSINESS", "Business", 499900, 2000, 14),
        ]
        changed = False
        for code, name, price_paise, limit, trial_days in defaults:
            if db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == code)) is None:
                db.add(SubscriptionPlan(code=code, name=name, price_paise=price_paise, monthly_review_limit=limit, trial_days=trial_days, is_active=True))
                changed = True
        if changed:
            db.commit()

    @staticmethod
    def plan(db: Session, code: str) -> SubscriptionPlan | None:
        BillingService.ensure_plans(db)
        return db.scalar(select(SubscriptionPlan).where(SubscriptionPlan.code == code.upper()))

    @staticmethod
    def subscription(db: Session, business_id: int) -> Subscription:
        BillingService.ensure_plans(db)
        sub = db.scalar(select(Subscription).where(Subscription.business_id == business_id))
        if sub is None:
            now=datetime.now(timezone.utc).replace(tzinfo=None)
            sub=Subscription(business_id=business_id, plan='STARTER', status='TRIALING', provider='MOCK', trial_ends_at=now+timedelta(days=14), current_period_start=now, current_period_end=now+timedelta(days=14))
            db.add(sub); db.commit(); db.refresh(sub)
        return sub
    @staticmethod
    def within_usage_limit(db: Session, business_id: int) -> bool:
        sub=BillingService.subscription(db,business_id)
        start=datetime.now(timezone.utc).replace(day=1,hour=0,minute=0,second=0,microsecond=0,tzinfo=None)
        used=int(db.scalar(select(func.count(GeneratedPositiveReview.id)).where(GeneratedPositiveReview.business_id==business_id, GeneratedPositiveReview.created_at>=start)) or 0)
        plan = BillingService.plan(db, sub.plan)
        limit = plan.monthly_review_limit if plan else PLANS.get(sub.plan, PLANS['STARTER'])['monthly_review_limit']
        return used < limit

    @staticmethod
    def checkout(db: Session, business_id: int, plan: str):
        db_plan = BillingService.plan(db, plan)
        if db_plan is None or not db_plan.is_active: raise ValueError('Invalid or inactive plan')
        amount=db_plan.price_paise; receipt=f'RA-{uuid.uuid4().hex[:16].upper()}'
        payment=BillingPayment(business_id=business_id,plan=plan,amount_paise=amount,currency='INR',status='CREATED',provider='MOCK',provider_payment_id=None,receipt_reference=receipt)
        db.add(payment); db.commit(); db.refresh(payment)
        return payment, f'mock_order_{payment.id}_{uuid.uuid4().hex[:8]}'
    @staticmethod
    def confirm(db: Session, payment_id: int, success: bool):
        payment=db.get(BillingPayment,payment_id)
        if not payment: raise ValueError('Payment not found')
        if payment.status not in {'CREATED','FAILED'}: return payment
        payment.status='PAID' if success else 'FAILED'
        if success:
            sub=BillingService.subscription(db,payment.business_id); now=datetime.now(timezone.utc).replace(tzinfo=None)
            sub.plan=payment.plan; sub.status='ACTIVE'; sub.current_period_start=now; sub.current_period_end=now+timedelta(days=30); sub.cancel_at_period_end=False
            payment.provider_payment_id=f'mock_payment_{payment.id}'
        db.commit(); db.refresh(payment); return payment
