import time
import uuid
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_logger

logger = get_logger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Adds request_id and timing to every request.
    Logs every request with method, path, status code and duration.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Store on request state so routes can access it
        request.state.request_id = request_id

        # Extract tenant context from JWT if present
        # We do this here so every log line has tenant context
        tenant_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.auth.jwt import decode_token
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                if payload:
                    tenant_id = payload.get("tenant_id")
                    request.state.tenant_id = tenant_id
            except Exception:
                pass  # Auth failures are handled by the auth dependency

        start_time = time.time()

        # Process the request
        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log every request as structured JSON
        extra = {
            "request_id": request_id,
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }
        if tenant_id:
            extra["tenant_id"] = tenant_id

        # Add request_id to response headers so clients can trace requests
        response.headers["X-Request-ID"] = request_id

        log_level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(log_level, "request completed", extra=extra)

        return response