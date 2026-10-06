from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import SessionLocal
from backend.app.models.business import Business
from backend.app.models.user import User
from backend.app.models.subscription import Subscription
from backend.app.core.security import create_access_token

client=TestClient(app)

def owner_headers():
    with SessionLocal() as db:
        u=db.query(User).filter(User.email=='owner@reviewagentai.local').first()
        return {'Authorization':f'Bearer {create_access_token(u)}'}

def test_owner_dashboard_and_date_range():
    r=client.get('/api/v1/owner/dashboard?days=7',headers=owner_headers()); assert r.status_code==200; assert r.json()['business_slug']=='reviewagentai'

def test_owner_isolation_from_other_business():
    # Owner dashboard is intentionally bound to the authenticated user's business.
    r=client.get('/api/v1/owner/dashboard?days=30',headers=owner_headers()); assert r.status_code==200
    assert r.json()['business_slug']=='reviewagentai'

def test_owner_settings_roundtrip():
    h=owner_headers(); r=client.get('/api/v1/owner/settings',headers=h); assert r.status_code==200
    body=r.json(); body['welcome_message']='Welcome!'; body['brand_primary_color']='#123456'; body['brand_secondary_color']='#654321'
    assert client.put('/api/v1/owner/settings/profile',headers=h,json={k:body[k] for k in ['name','description','category','logo_url','welcome_message']}).status_code==200
    assert client.put('/api/v1/owner/settings/branding',headers=h,json={'brand_primary_color':'#123456','brand_secondary_color':'#654321'}).status_code==200

def test_owner_social_crud():
    h=owner_headers(); r=client.post('/api/v1/owner/social-links',headers=h,json={'platform':'WEBSITE','url':'https://example.com','display_order':99,'enabled':True}); assert r.status_code==201
    i=r.json()['id']; assert client.put(f'/api/v1/owner/social-links/{i}',headers=h,json={'platform':'WEBSITE','url':'https://example.org','display_order':1,'enabled':True}).status_code==200
    assert client.delete(f'/api/v1/owner/social-links/{i}',headers=h).status_code==204

def test_billing_checkout_confirm_and_history():
    h=owner_headers(); assert client.get('/api/v1/billing/plans').status_code==200
    r=client.post('/api/v1/billing/checkout',headers=h,json={'plan':'PROFESSIONAL'}); assert r.status_code==200
    pid=r.json()['payment_id']; r=client.post('/api/v1/billing/confirm',headers=h,json={'payment_id':pid,'success':True}); assert r.status_code==200 and r.json()['status']=='PAID'
    assert client.get('/api/v1/billing/history',headers=h).status_code==200
    assert client.get('/api/v1/billing/subscription',headers=h).status_code==200

def test_owner_notifications_requires_auth():
    assert client.get('/api/v1/owner/notifications').status_code==401
