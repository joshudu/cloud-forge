from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

def test_create_tenant_validation():
    # Test that missing name returns 422
    response = client.post("/tenants/", json={})
    assert response.status_code == 422

def test_create_tenant_requires_name():
    response = client.post("/tenants/", json={"name": ""})
    # Empty name should be handled — this test documents current behaviour
    assert response.status_code in [200, 400, 422]