from fastapi.testclient import TestClient
from app.main import app
from app.core.resilience import CircuitBreaker

client = TestClient(app)

def test_circuit_breaker_opens_after_failures():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
    assert cb.state == CircuitBreaker.CLOSED
    assert cb.can_attempt() == True

    # Simulate failures
    cb.call_failed()
    cb.call_failed()
    assert cb.state == CircuitBreaker.CLOSED

    cb.call_failed()
    assert cb.state == CircuitBreaker.OPEN
    assert cb.can_attempt() == False

def test_circuit_breaker_closes_after_success():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0)
    cb.call_failed()
    cb.call_failed()
    assert cb.state == CircuitBreaker.OPEN

    # Force half-open by setting recovery_timeout to 0
    cb.recovery_timeout = 0
    assert cb.can_attempt() == True

    cb.call_succeeded()
    assert cb.state == CircuitBreaker.CLOSED

def test_app_health_endpoints_stable():
    for _ in range(10):
        response = client.get("/health/live")
        assert response.status_code == 200