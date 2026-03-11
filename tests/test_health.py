from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_liveness():
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}

def test_readiness_returns_valid_response():
    response = client.get("/health/ready")
    # Either ready (200) or not ready (503) are both valid responses
    assert response.status_code in [200, 503]

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_request_id_in_response_headers():
    response = client.get("/health/live")
    assert "x-request-id" in response.headers