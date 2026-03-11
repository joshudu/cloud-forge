import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.auth.dependencies import get_current_user_payload, get_tenant_db

# Mock payload representing an authenticated user
MOCK_PAYLOAD = {
    "sub": "test@example.com",
    "tenant_id": "123e4567-e89b-12d3-a456-426614174000",
    "schema": "tenant_test_corp",
    "type": "access"
}

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def authenticated_client():
    """Client with mocked authentication — no real JWT needed in tests"""
    app.dependency_overrides[get_current_user_payload] = lambda: MOCK_PAYLOAD
    app.dependency_overrides[get_tenant_db] = lambda: AsyncMock()
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()