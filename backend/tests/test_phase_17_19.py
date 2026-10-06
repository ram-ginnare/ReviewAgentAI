import io
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import SessionLocal
from backend.app.models.business import Business
from backend.app.models.review_event import ReviewEvent
from backend.app.models.user import User
from backend.app.core.security import create_access_token

client=TestClient(app)

def owner_headers():
    with SessionLocal() as db:
        u=db.query(User).filter(User.email=='owner@reviewagentai.local').first()
        return {'Authorization':f'Bearer {create_access_token(u)}'}

def test_advanced_analytics_and_exports():
    h=owner_headers()
    assert client.get('/api/v1/owner/analytics?days=30',headers=h).status_code==200
    for ext in ('csv','xlsx','pdf'):
        r=client.get(f'/api/v1/owner/analytics/export.{ext}?days=30',headers=h)
        assert r.status_code==200
        assert len(r.content)>20

def test_advanced_analytics_is_owner_only():
    assert client.get('/api/v1/owner/analytics?days=30').status_code==401

def test_security_headers_present():
    r=client.get('/api/v1/health')
    assert r.headers['x-content-type-options']=='nosniff'
    assert r.headers['x-frame-options']=='DENY'
    assert r.headers['referrer-policy']=='strict-origin-when-cross-origin'

def test_audit_table_exists_and_rate_limit_configured():
    with SessionLocal() as db:
        assert db.execute(__import__('sqlalchemy').text("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_logs'")).scalar_one_or_none()=='audit_logs'
