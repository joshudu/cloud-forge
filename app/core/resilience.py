import asyncio
import logging
from functools import wraps
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError
)
from sqlalchemy.exc import OperationalError, DisconnectionError
from app.core.logging import get_logger

logger = get_logger(__name__)

def db_retry(func):
    """
    Decorator that adds retry logic with exponential backoff
    to database operations.

    Retries up to 3 times with exponential backoff:
    - First retry: wait 1 second
    - Second retry: wait 2 seconds
    - Third retry: wait 4 seconds

    Only retries on connection errors, not on data errors.
    This is important — you never want to retry a write operation
    that may have partially succeeded.
    """
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((OperationalError, DisconnectionError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper


class CircuitBreaker:
    """
    Simple circuit breaker implementation.

    States:
    - CLOSED: normal operation, requests go through
    - OPEN: too many failures, requests blocked immediately
    - HALF_OPEN: testing if service recovered

    The circuit opens after 5 consecutive failures.
    After 30 seconds it moves to HALF_OPEN and tries one request.
    If that succeeds it closes again. If it fails it reopens.
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = self.CLOSED

    def call_succeeded(self):
        self.failure_count = 0
        self.state = self.CLOSED
        logger.info("circuit breaker closed — service recovered")

    def call_failed(self):
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()
        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN
            logger.warning(
                f"circuit breaker opened after {self.failure_count} failures"
            )

    def can_attempt(self) -> bool:
        if self.state == self.CLOSED:
            return True
        if self.state == self.OPEN:
            time_since_failure = (
                asyncio.get_event_loop().time() - self.last_failure_time
            )
            if time_since_failure >= self.recovery_timeout:
                self.state = self.HALF_OPEN
                logger.info("circuit breaker half-open — testing recovery")
                return True
            return False
        if self.state == self.HALF_OPEN:
            return True
        return False

# Global circuit breaker for database operations
db_circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)