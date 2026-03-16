import json
import os
from typing import Optional, Any
from app.core.logging import get_logger

logger = get_logger(__name__)

# Redis client — initialized lazily so tests don't need Redis
_redis_client = None

async def get_redis():
    """
    Get or create Redis client.
    Returns None if Redis is not configured — app works without cache.
    This is the graceful degradation pattern.
    """
    global _redis_client

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return None

    if _redis_client is None:
        try:
            import redis.asyncio as redis
            _redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await _redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis unavailable — running without cache: {str(e)}")
            return None

    return _redis_client


def make_cache_key(tenant_schema: str, resource: str, identifier: str = "") -> str:
    """
    Generate a consistent cache key.
    Always scoped to tenant to prevent cross-tenant cache leaks.

    Examples:
    - tenant_acme:projects:all
    - tenant_acme:projects:uuid-123
    - tenant_acme:user:user@example.com
    """
    if identifier:
        return f"{tenant_schema}:{resource}:{identifier}"
    return f"{tenant_schema}:{resource}"


async def cache_get(key: str) -> Optional[Any]:
    """Get a value from cache. Returns None on miss or error."""
    redis = await get_redis()
    if redis is None:
        return None
    try:
        value = await redis.get(key)
        if value:
            logger.info(f"cache hit", extra={"cache_key": key})
            return json.loads(value)
        logger.info(f"cache miss", extra={"cache_key": key})
        return None
    except Exception as e:
        logger.warning(f"cache get failed: {str(e)}")
        return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """
    Set a value in cache with TTL in seconds.
    Default TTL is 5 minutes.
    Returns False on error — caller should handle gracefully.
    """
    redis = await get_redis()
    if redis is None:
        return False
    try:
        await redis.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.warning(f"cache set failed: {str(e)}")
        return False


async def cache_invalidate(pattern: str) -> int:
    """
    Invalidate all cache keys matching a pattern.
    Returns number of keys deleted.
    Use carefully — pattern matching is expensive on large caches.
    """
    redis = await get_redis()
    if redis is None:
        return 0
    try:
        keys = await redis.keys(pattern)
        if keys:
            deleted = await redis.delete(*keys)
            logger.info(
                f"cache invalidated",
                extra={"pattern": pattern, "keys_deleted": deleted}
            )
            return deleted
        return 0
    except Exception as e:
        logger.warning(f"cache invalidation failed: {str(e)}")
        return 0