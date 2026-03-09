from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_missing_fields():
    response = client.post("/auth/register", json={})
    assert response.status_code == 422

def test_register_invalid_email():
    response = client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "password123",
        "tenant_name": "Test Corp"
    })
    assert response.status_code == 422

def test_refresh_invalid_token():
    response = client.post("/auth/refresh", json={
        "refresh_token": "this.is.not.valid"
    })
    assert response.status_code == 401