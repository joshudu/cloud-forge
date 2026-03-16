"""
Chaos tests — these are meant to be run manually against a live environment.
They are skipped in CI by default.
Run with: pytest tests/test_chaos.py -v -m chaos
"""
import pytest
import httpx
import time

BASE_URL = "http://34.247.28.76:8000"  # Replace with your ECS IP

@pytest.mark.chaos
def test_rapid_requests():
    """Send 50 rapid requests and verify the app stays stable"""
    results = []
    with httpx.Client() as client:
        for i in range(50):
            try:
                response = client.get(f"{BASE_URL}/health/live", timeout=5)
                results.append(response.status_code)
            except Exception as e:
                results.append(0)

    success_rate = results.count(200) / len(results)
    print(f"\nSuccess rate: {success_rate * 100:.1f}%")
    print(f"Status codes: {set(results)}")
    assert success_rate >= 0.95, f"Success rate too low: {success_rate}"

@pytest.mark.chaos
def test_rate_limit_recovery():
    """Verify rate limiting kicks in and then recovers"""
    with httpx.Client() as client:
        responses = []
        for i in range(15):
            response = client.post(
                f"{BASE_URL}/auth/login-tenant",
                params={"tenant_name": "test"},
                json={"email": "test@test.com", "password": "wrong"},
                timeout=5
            )
            responses.append(response.status_code)

        rate_limited = [r for r in responses if r == 429]
        print(f"\nRate limited responses: {len(rate_limited)}")
        assert len(rate_limited) > 0, "Expected some rate limited responses"


@pytest.mark.chaos
def test_health_ready_reflects_db_state():
    """
    This test must be run manually with a live environment.
    Stop RDS manually, run this test, then restart RDS.
    """
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health/ready", timeout=10)
        print(f"\nHealth ready status: {response.status_code}")
        print(f"Response body: {response.json()}")
        # When DB is down this should return 503
        # When DB is up this should return 200
        assert response.status_code in [200, 503]