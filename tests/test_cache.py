import pytest
from unittest.mock import AsyncMock, patch
from app.core.cache import make_cache_key, cache_get, cache_set, cache_invalidate

def test_cache_key_format():
    key = make_cache_key("tenant_acme", "projects", "all")
    assert key == "tenant_acme:projects:all"

def test_cache_key_without_identifier():
    key = make_cache_key("tenant_acme", "projects")
    assert key == "tenant_acme:projects"

def test_cache_key_is_tenant_scoped():
    key1 = make_cache_key("tenant_acme", "projects", "all")
    key2 = make_cache_key("tenant_other", "projects", "all")
    assert key1 != key2

@pytest.mark.asyncio
async def test_cache_get_returns_none_when_redis_unavailable():
    with patch("app.core.cache.get_redis", return_value=AsyncMock(return_value=None)):
        result = await cache_get("some:key")
        assert result is None

@pytest.mark.asyncio
async def test_cache_set_returns_false_when_redis_unavailable():
    with patch("app.core.cache.get_redis", return_value=AsyncMock(return_value=None)):
        result = await cache_set("some:key", {"data": "value"})
        assert result is False