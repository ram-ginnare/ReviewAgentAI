from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["application"] == "reviewagentai"

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"
    assert response.json()["database"] == "UP"

def test_business_endpoint_returns_seed_business():
    response = client.get("/api/v1/businesses/abc-restaurant")
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "abc-restaurant"
    assert body["name"] == "ABC Restaurant"
    assert len(body["social_links"]) == 5

def test_unknown_business_returns_404():
    response = client.get("/api/v1/businesses/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Business not found"
