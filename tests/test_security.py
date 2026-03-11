from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cors_headers_present():
    response = client.get(
        "/health/live",
        headers={"Origin": "http://localhost:3000"}
    )
    assert response.status_code == 200

def test_request_id_always_present():
    response = client.get("/health/live")
    assert "x-request-id" in response.headers

def test_admin_erasure_requires_auth():
    import uuid
    response = client.delete(f"/admin/tenants/{uuid.uuid4()}")
    assert response.status_code == 401

def test_protected_routes_require_auth():
    response = client.get("/projects/")
    assert response.status_code == 401

    response = client.get("/resources/project/some-id")
    assert response.status_code == 401