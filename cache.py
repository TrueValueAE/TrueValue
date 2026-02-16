"""
Redis Caching Layer for TrueValue AI
======================================
Provides transparent caching for tool results with configurable TTLs.
Graceful degradation: works without Redis (all ops return None / no-op).
"""

import os
import json
import hashlib
import logging
from typing import Optional, Any

logger = logging.getLogger("cache")

_redis = None

# TTL configuration per tool (seconds)
CACHE_TTLS = {
    "search_bayut_properties": 3600,      # 1 hour
    "get_market_trends": 3600,            # 1 hour
    "get_supply_pipeline": 86400,         # 24 hours
    "web_search_dubai": 1800,             # 30 minutes
    "search_building_issues": 86400,      # 24 hours
    "get_dld_transactions": 86400,        # 24 hours
    "get_rental_comps": 3600,             # 1 hour
    # No cache for these:
    # calculate_chiller_cost — instant math, no external call
    # analyze_investment — composite, depends on cached sub-tools
    # verify_title_deed — must be live for legal accuracy
    # compare_properties — composite
}


async def init_cache(redis_url: Optional[str] = None) -> None:
    """Initialise the Redis connection."""
    global _redis

    url = redis_url or os.getenv("REDIS_URL", "")
    if not url:
        logger.info("REDIS_URL not set — caching disabled")
        return

    try:
        import redis.asyncio as aioredis
        _redis = aioredis.from_url(url, decode_responses=True, socket_timeout=2)
        # Test connection
        await _redis.ping()
        logger.info("Redis cache connected at %s", url)
    except Exception as exc:
        logger.warning("Redis connection failed (%s) — caching disabled", exc)
        _redis = None


async def close_cache() -> None:
    """Close the Redis connection."""
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


def is_cache_available() -> bool:
    """Check if Redis is connected."""
    return _redis is not None


def _make_key(tool_name: str, params: dict) -> str:
    """Create a deterministic cache key from tool name and params."""
    param_str = json.dumps(params, sort_keys=True, default=str)
    param_hash = hashlib.md5(param_str.encode()).hexdigest()[:12]
    return f"tv:{tool_name}:{param_hash}"


async def get_cached(tool_name: str, params: dict) -> Optional[Any]:
    """
    Get a cached tool result.
    Returns None if not cached, cache disabled, or tool not cacheable.
    """
    if not _redis or tool_name not in CACHE_TTLS:
        return None

    try:
        key = _make_key(tool_name, params)
        data = await _redis.get(key)
        if data:
            logger.debug("Cache HIT: %s", key)
            return json.loads(data)
        logger.debug("Cache MISS: %s", key)
        return None
    except Exception as exc:
        logger.debug("Cache get error: %s", exc)
        return None


async def set_cached(tool_name: str, params: dict, result: Any, ttl: Optional[int] = None) -> None:
    """
    Cache a tool result with TTL.
    No-op if cache disabled or tool not cacheable.
    """
    if not _redis or tool_name not in CACHE_TTLS:
        return

    effective_ttl = ttl or CACHE_TTLS.get(tool_name, 3600)

    try:
        key = _make_key(tool_name, params)
        await _redis.setex(key, effective_ttl, json.dumps(result, default=str))
        logger.debug("Cache SET: %s (TTL=%ds)", key, effective_ttl)
    except Exception as exc:
        logger.debug("Cache set error: %s", exc)


async def invalidate(tool_name: str, params: dict) -> None:
    """Remove a specific cache entry."""
    if not _redis:
        return

    try:
        key = _make_key(tool_name, params)
        await _redis.delete(key)
    except Exception:
        pass


async def flush_all() -> None:
    """Flush all TrueValue cache entries."""
    if not _redis:
        return

    try:
        keys = []
        async for key in _redis.scan_iter("tv:*"):
            keys.append(key)
        if keys:
            await _redis.delete(*keys)
            logger.info("Flushed %d cache entries", len(keys))
    except Exception as exc:
        logger.warning("Cache flush error: %s", exc)
