from locust import HttpUser, task, between
import json

class CloudForgeUser(HttpUser):
    """
    Simulates a CloudForge user making typical API calls.
    Wait 1-3 seconds between tasks to simulate real user behaviour.
    """
    wait_time = between(1, 3)
    token = None
    tenant_name = "loadtest-tenant"

    def on_start(self):
        """Called when a simulated user starts — register and login."""
        # Register
        response = self.client.post("/auth/register", json={
            "email": f"user_{id(self)}@loadtest.com",
            "password": "loadtest123",
            "tenant_name": self.tenant_name
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")

    def get_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    @task(3)
    def list_projects(self):
        """Most common operation — list projects (cached after first call)"""
        self.client.get("/projects/", headers=self.get_headers())

    @task(1)
    def create_project(self):
        """Less common — create a project"""
        import uuid
        self.client.post(
            "/projects/",
            json={
                "name": f"Load Test Project {uuid.uuid4()}",
                "description": "Created during load test"
            },
            headers=self.get_headers()
        )

    @task(5)
    def health_check(self):
        """Health checks — highest frequency"""
        self.client.get("/health/live")

    @task(2)
    def get_root(self):
        self.client.get("/")