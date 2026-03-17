import os
from app.core.logging import get_logger

logger = get_logger(__name__)

def setup_xray():
    """
    Configure AWS X-Ray tracing.
    Only enabled in non-local environments.
    Gracefully skips if X-Ray SDK is unavailable.
    """
    if os.getenv("ENVIRONMENT", "local") == "local":
        logger.info("X-Ray tracing disabled in local environment")
        return

    try:
        from aws_xray_sdk.core import xray_recorder, patch_all
        from aws_xray_sdk.core import patch

        xray_recorder.configure(
            service="cloudforge",
            sampling=True,
            context_missing="LOG_ERROR",
            plugins=("ECSPlugin",),
        )

        # Patch AWS SDK calls so they appear in traces
        patch(["boto3", "botocore"])

        logger.info("X-Ray tracing enabled")

    except Exception as e:
        logger.warning(f"X-Ray setup failed — running without tracing: {str(e)}")


def get_xray_middleware():
    """
    Returns X-Ray middleware for FastAPI.
    Returns None if X-Ray is not available or not configured.
    """
    if os.getenv("ENVIRONMENT", "local") == "local":
        return None

    try:
        from aws_xray_sdk.ext.fastapi.middleware import XRayMiddleware
        return XRayMiddleware
    except Exception:
        return None