from tests.conftest import MOCK_PAYLOAD

def test_create_project_missing_name(authenticated_client):
    response = authenticated_client.post("/projects/", json={})
    assert response.status_code == 422

def test_create_project_empty_name(authenticated_client):
    response = authenticated_client.post("/projects/", json={"name": ""})
    assert response.status_code == 422

def test_create_project_name_too_long(authenticated_client):
    response = authenticated_client.post("/projects/", json={"name": "x" * 256})
    assert response.status_code == 422

def test_get_nonexistent_project(client):
    # Without auth — should get 401 not 404
    response = client.get("/projects/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 401