from backend.app.core.security import hash_password, verify_password
from backend.app.db.database import SessionLocal
from backend.app.models.user import User
from fastapi.testclient import TestClient
from backend.app.main import app


def test_password_hash_is_not_plaintext():
    encoded = hash_password("StrongPass123!")
    assert encoded != "StrongPass123!"
    assert verify_password("StrongPass123!", encoded)
    assert not verify_password("WrongPass123!", encoded)


def test_demo_users_exist_and_roles_are_scoped():
    with SessionLocal() as db:
        admin = db.query(User).filter_by(email="admin@reviewagentai.local").one()
        owner = db.query(User).filter_by(email="owner@reviewagentai.local").one()
        assert admin.role == "ADMIN"
        assert admin.business_id is None
        assert owner.role == "BUSINESS_OWNER"
        assert owner.business_id is not None


def test_login_and_me():
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/login", json={"email": "owner@reviewagentai.local", "password": "Owner@12345"})
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["user"]["role"] == "BUSINESS_OWNER"
        me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {data['access_token']}"})
        assert me.status_code == 200
        assert me.json()["email"] == "owner@reviewagentai.local"


def test_invalid_login_is_rejected():
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/login", json={"email": "owner@reviewagentai.local", "password": "WrongPass123!"})
        assert response.status_code == 401
        assert response.json()["code"] == "INVALID_CREDENTIALS"


def test_me_requires_authentication():
    with TestClient(app) as client:
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert response.json()["code"] == "AUTH_REQUIRED"


def test_change_password_round_trip():
    with TestClient(app) as client:
        login = client.post("/api/v1/auth/login", json={"email": "owner@reviewagentai.local", "password": "Owner@12345"})
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        changed = client.post("/api/v1/auth/change-password", json={"current_password": "Owner@12345", "new_password": "Owner@123456!"}, headers=headers)
        assert changed.status_code == 204
        again = client.post("/api/v1/auth/login", json={"email": "owner@reviewagentai.local", "password": "Owner@123456!"})
        assert again.status_code == 200
        # Restore deterministic demo credentials for later tests/runs.
        client.post("/api/v1/auth/change-password", json={"current_password": "Owner@123456!", "new_password": "Owner@12345"}, headers={"Authorization": f"Bearer {again.json()['access_token']}"})


def test_admin_can_list_users_and_non_admin_cannot():
    with TestClient(app) as client:
        admin_login = client.post("/api/v1/auth/login", json={"email": "admin@reviewagentai.local", "password": "Admin@12345"})
        admin_token = admin_login.json()["access_token"]
        response = client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        assert any(user["role"] == "BUSINESS_OWNER" for user in response.json())

        owner_login = client.post("/api/v1/auth/login", json={"email": "owner@reviewagentai.local", "password": "Owner@12345"})
        owner_token = owner_login.json()["access_token"]
        forbidden = client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {owner_token}"})
        assert forbidden.status_code == 403
        assert forbidden.json()["code"] == "ADMIN_REQUIRED"
