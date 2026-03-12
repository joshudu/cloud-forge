from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_starts_successfully():
    """Verify the app initialises without errors"""
    response = client.get("/")
    assert response.status_code == 200

def test_openapi_schema_accessible():
    """Verify API documentation is generated correctly"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/health/live" in schema["paths"]
    assert "/health/ready" in schema["paths"]
    assert "/auth/register" in schema["paths"]
    assert "/projects/" in schema["paths"]

def test_all_routes_registered():
    """Verify all expected routes exist"""
    response = client.get("/openapi.json")
    paths = response.json()["paths"]
    expected_paths = [
        "/health/live",
        "/health/ready",
        "/auth/register",
        "/auth/login-tenant",
        "/auth/refresh",
        "/projects/",
        "/resources/",
    ]
    for path in expected_paths:
        assert path in paths, f"Expected path {path} not found in API schema"