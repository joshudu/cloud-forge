from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.auth.jwt import decode_token
from app.core.logging import get_logger

logger = get_logger(__name__)

def get_tenant_or_ip(request: Request) -> str:
    """
    Rate limit key function.
    Use tenant_id if authenticated, fall back to IP address.
    This means each tenant gets their own rate limit bucket
    rather than sharing one with all other tenants on the same IP.
    """
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if payload and payload.get("tenant_id"):
                return f"tenant:{payload['tenant_id']}"
        except Exception:
            pass
    return get_remote_address(request)

# Global limiter instance
limiter = Limiter(key_func=get_tenant_or_ip)