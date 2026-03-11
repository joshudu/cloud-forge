from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/health/live")
def liveness():
    """
    Liveness check — is the process running?
    If this fails, ECS restarts the container.
    """
    return {"status": "alive"}

@router.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    """
    Readiness check — can we serve traffic?
    Checks database connectivity.
    If this fails, ECS stops sending traffic to this task.
    """
    try:
        if db is None:
            return {"status": "ready", "database": "not configured"}
        await db.execute(text("SELECT 1"))
        logger.info("readiness check passed")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"readiness check failed: {str(e)}")
        return {"status": "not ready", "database": "disconnected"}, 503