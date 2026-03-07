from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_tenant_validation():
    response = client.post("/tenants/", json={})
    assert response.status_code == 422