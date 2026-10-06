from fastapi.testclient import TestClient
from backend.app.main import app

ADMIN = {"email": "admin@reviewagentai.local", "password": "Admin@12345"}
OWNER = {"email": "owner@reviewagentai.local", "password": "Owner@12345"}


def login(client, payload):
    response = client.post('/api/v1/auth/login', json=payload)
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_can_list_plans_and_subscriptions():
    with TestClient(app) as client:
        headers = login(client, ADMIN)
        plans = client.get('/api/v1/admin/billing/plans', headers=headers)
        assert plans.status_code == 200
        assert {p['code'] for p in plans.json()} >= {'STARTER', 'PROFESSIONAL', 'BUSINESS'}
        subscriptions = client.get('/api/v1/admin/billing/subscriptions', headers=headers)
        assert subscriptions.status_code == 200
        assert any(s['business_slug'] == 'reviewagentai' for s in subscriptions.json())


def test_non_admin_cannot_manage_billing():
    with TestClient(app) as client:
        headers = login(client, OWNER)
        assert client.get('/api/v1/admin/billing/plans', headers=headers).status_code == 403
        assert client.get('/api/v1/admin/billing/subscriptions', headers=headers).status_code == 403


def test_admin_can_update_plan_details_and_owner_sees_them():
    with TestClient(app) as client:
        admin = login(client, ADMIN)
        owner = login(client, OWNER)
        before = client.get('/api/v1/admin/billing/plans', headers=admin).json()
        starter = next(p for p in before if p['code'] == 'STARTER')
        original = dict(starter)
        updated = dict(starter, name='Starter Admin Test', price_paise=123400, monthly_review_limit=321, trial_days=21, is_active=True)
        response = client.put('/api/v1/admin/billing/plans/STARTER', json=updated, headers=admin)
        assert response.status_code == 200
        plans = client.get('/api/v1/billing/plans', headers=owner)
        assert plans.status_code == 200
        starter_after = next(p for p in plans.json() if p['code'] == 'STARTER')
        assert starter_after['price_paise'] == 123400
        assert starter_after['monthly_review_limit'] == 321
        assert starter_after['name'] == 'Starter Admin Test'
        # Restore deterministic defaults.
        client.put('/api/v1/admin/billing/plans/STARTER', json={
            'name': original['name'], 'price_paise': original['price_paise'],
            'monthly_review_limit': original['monthly_review_limit'], 'trial_days': original['trial_days'], 'is_active': True,
        }, headers=admin)


def test_admin_can_change_business_subscription():
    with TestClient(app) as client:
        admin = login(client, ADMIN)
        rows = client.get('/api/v1/admin/billing/subscriptions', headers=admin).json()
        business = next(s for s in rows if s['business_slug'] == 'reviewagentai')
        response = client.put(f"/api/v1/admin/billing/subscriptions/{business['business_id']}", json={
            'plan': 'PROFESSIONAL', 'status': 'ACTIVE', 'trial_ends_at': None,
            'current_period_start': '2026-09-19T00:00:00', 'current_period_end': '2026-10-19T00:00:00',
            'cancel_at_period_end': False,
        }, headers=admin)
        assert response.status_code == 200
        assert response.json()['plan'] == 'PROFESSIONAL'
        assert response.json()['status'] == 'ACTIVE'

        # Restore the demo subscription.
        client.put(f"/api/v1/admin/billing/subscriptions/{business['business_id']}", json={
            'plan': 'STARTER', 'status': 'TRIALING', 'trial_ends_at': '2026-10-03T00:00:00',
            'current_period_start': None, 'current_period_end': None, 'cancel_at_period_end': False,
        }, headers=admin)
