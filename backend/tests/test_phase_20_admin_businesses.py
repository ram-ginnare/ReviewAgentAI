from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.business import Business
from backend.app.core.security import hash_password

def auth(client, email, password):
    r=client.post('/api/v1/auth/login',json={'email':email,'password':password}); assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['access_token']}

def test_admin_can_list_businesses_and_owners():
    with TestClient(app) as client:
        headers=auth(client,'admin@reviewagentai.local','Admin@12345')
        r=client.get('/api/v1/admin/businesses',headers=headers)
        assert r.status_code==200
        data=r.json(); assert 'businesses' in data and 'owners' in data
        assert isinstance(data['businesses'],list) and isinstance(data['owners'],list)

def test_business_owner_cannot_access_admin_businesses():
    with TestClient(app) as client:
        headers=auth(client,'owner@reviewagentai.local','Owner@12345')
        assert client.get('/api/v1/admin/businesses',headers=headers).status_code==403

def test_admin_can_create_update_and_toggle_business():
    with TestClient(app) as client:
        headers=auth(client,'admin@reviewagentai.local','Admin@12345')
        unique_email='phase20-owner-test@reviewagentai.local'
        test_slug='phase20-test-business'
        # Keep this integration test repeatable against the project's persistent SQLite DB.
        # The production API correctly rejects duplicate slugs with HTTP 409; the test
        # must remove leftovers from an earlier pytest run before exercising creation.
        with SessionLocal() as db:
            existing_business=db.query(Business).filter_by(slug=test_slug).first()
            if existing_business:
                db.delete(existing_business)
                db.commit()
            existing=db.query(User).filter_by(email=unique_email).first()
            if existing:
                db.delete(existing)
                db.commit()
            temp_owner=User(email=unique_email,password_hash=hash_password('Phase20@12345'),full_name='Phase 20 Owner',role='BUSINESS_OWNER',business_id=None,is_active=True)
            db.add(temp_owner); db.commit(); db.refresh(temp_owner); owner_id=temp_owner.id
        payload={'slug':test_slug,'name':'Phase 20 Demo','description':'Admin-created business','category':'Demo','google_review_pc_url':'https://example.com/pc','google_review_mob_url':'https://example.com/mobile','status':'ACTIVE','prefer_ai_comments':False,'brand_primary_color':'#123456','brand_secondary_color':'#654321','nfc_enabled':False,'qr_enabled':True,'customer_settings':{'show_welcome':True},'social_links':[{'platform':'WEBSITE','url':'https://example.com','display_order':1,'enabled':True}]}
        created=client.post('/api/v1/admin/businesses',json=payload,headers=headers); assert created.status_code==201,created.text
        bid=created.json()['id']; assert created.json()['plan']=='STARTER'
        update=dict(payload); update.update({'name':'Phase 20 Updated','owner_id':owner_id,'status':'INACTIVE'})
        updated=client.put(f'/api/v1/admin/businesses/{bid}',json=update,headers=headers); assert updated.status_code==200,updated.text
        assert updated.json()['name']=='Phase 20 Updated' and updated.json()['owner_id']==owner_id
        toggled=client.patch(f'/api/v1/admin/businesses/{bid}/status?active=true',headers=headers); assert toggled.status_code==200, toggled.text
        assert toggled.json()['status']=='ACTIVE'
