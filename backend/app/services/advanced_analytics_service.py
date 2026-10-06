from datetime import datetime, timedelta, timezone
from sqlalchemy import func, select, case
from sqlalchemy.orm import Session
from backend.app.models.business import Business
from backend.app.models.review_event import ReviewEvent
from backend.app.models.complaint import LocalComplaint

class AdvancedAnalyticsService:
    @staticmethod
    def _business(db: Session, business_id: int) -> Business:
        b = db.get(Business, business_id)
        if not b or b.status != 'ACTIVE':
            raise ValueError('Business not found or inactive')
        return b

    @staticmethod
    def report(db: Session, business_id: int, days: int = 30) -> dict:
        b = AdvancedAnalyticsService._business(db, business_id)
        since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
        base = [ReviewEvent.business_id == b.id, ReviewEvent.created_at >= since]
        events = db.scalars(select(ReviewEvent).where(*base).order_by(ReviewEvent.created_at)).all()
        counts = {}
        ratings = {str(i): 0 for i in range(1, 6)}
        sources = {'qr': 0, 'nfc': 0, 'direct': 0}
        ai = fallback = 0
        for e in events:
            counts[e.event_type] = counts.get(e.event_type, 0) + 1
            if e.rating in range(1, 6): ratings[str(e.rating)] += 1
            meta = e.event_metadata or {}
            source = str(meta.get('source', '')).lower()
            if source in sources: sources[source] += 1
            if e.event_type == 'AI_REVIEWS_GENERATED': ai += 1
            if e.event_type == 'REVIEW_SELECTED' and str(meta.get('generation_mode','')).upper() == 'FALLBACK': fallback += 1
        complaints = db.scalar(select(func.count(LocalComplaint.id)).where(LocalComplaint.business_id==b.id, LocalComplaint.created_at>=since)) or 0
        positive = ratings['4'] + ratings['5']; negative = ratings['1'] + ratings['2']
        rating_total = sum(ratings.values())
        handoffs = counts.get('GOOGLE_HANDOFF', 0)
        rating_selections = counts.get('RATING_SELECTED', 0)
        monthly = []
        for i in range(min(days, 365) // 30 + 1):
            end = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=30*i)
            start = end - timedelta(days=30)
            row = db.execute(select(func.count(ReviewEvent.id)).where(ReviewEvent.business_id==b.id, ReviewEvent.created_at>=start, ReviewEvent.created_at<end)).scalar_one()
            monthly.append({'period': start.strftime('%Y-%m'), 'events': int(row)})
        monthly.reverse()
        return {
            'business_id': b.id, 'business_slug': b.slug, 'period_days': days,
            'total_events': len(events), 'event_counts': counts, 'rating_counts': ratings,
            'positive_reviews': positive, 'negative_reviews': negative,
            'positive_ratio': round(positive/rating_total*100,2) if rating_total else 0.0,
            'negative_ratio': round(negative/rating_total*100,2) if rating_total else 0.0,
            'complaints': int(complaints), 'google_handoffs': handoffs,
            'google_handoff_rate': round(handoffs/rating_selections*100,2) if rating_selections else 0.0,
            'source_counts': sources, 'ai_usage': ai, 'fallback_usage': fallback,
            'monthly_trend': monthly,
        }
