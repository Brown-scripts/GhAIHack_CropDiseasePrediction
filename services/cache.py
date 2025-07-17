"""
Enhanced caching system with Redis support and fallback to in-memory cache
Provides TTL management, cache invalidation, and performance monitoring
"""
import json
import logging
import asyncio
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import pickle
import hashlib

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from cachetools import TTLCache
from config.settings import settings
from config.logging import get_logger

logger = get_logger("cache")


class CacheManager:
    """Enhanced cache manager with Redis and in-memory fallback"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache = TTLCache(maxsize=1000, ttl=settings.cache_ttl_default)
        self.redis_enabled = settings.redis_enabled and REDIS_AVAILABLE
        self.stats = {
            "hits": 0,
            "misses": 0,
            "redis_hits": 0,
            "memory_hits": 0,
            "errors": 0
        }

    async def init_redis(self):
        """Initialize Redis connection"""
        if not self.redis_enabled:
            logger.info("Redis caching disabled or not available")
            return

        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=10,
                socket_timeout=10,
                retry_on_timeout=True,
                health_check_interval=30,
                max_connections=20
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_enabled = False
            self.redis_client = None

    async def close_redis(self):
        """Close Redis connection"""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")

    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            return pickle.dumps(value)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise

    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            raise

    def _generate_cache_key(self, key: str, prefix: str = "crop_api") -> str:
        """Generate a standardized cache key"""
        # Create a hash for very long keys
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        return f"{prefix}:{key}"

    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache (Redis first, then memory)"""
        cache_key = self._generate_cache_key(key)

        # Try Redis first
        if self.redis_enabled and self.redis_client:
            try:
                data = await self.redis_client.get(cache_key)
                if data is not None:
                    value = self._deserialize_value(data)
                    self.stats["hits"] += 1
                    self.stats["redis_hits"] += 1
                    logger.debug(f"Cache hit (Redis): {key}")
                    return value
            except Exception as e:
                logger.error(f"Redis get error for key {key}: {e}")
                self.stats["errors"] += 1

        # Try memory cache
        value = self.memory_cache.get(cache_key, default)
        if value is not default:
            self.stats["hits"] += 1
            self.stats["memory_hits"] += 1
            logger.debug(f"Cache hit (Memory): {key}")
            return value

        # Cache miss
        self.stats["misses"] += 1
        logger.debug(f"Cache miss: {key}")
        return default

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        cache_key = self._generate_cache_key(key)
        ttl = ttl or settings.cache_ttl_default

        success = False

        # Set in Redis
        if self.redis_enabled and self.redis_client:
            try:
                serialized_value = self._serialize_value(value)
                await self.redis_client.setex(cache_key, ttl, serialized_value)
                success = True
                logger.debug(f"Cache set (Redis): {key}, TTL: {ttl}")
            except Exception as e:
                logger.error(f"Redis set error for key {key}: {e}")
                self.stats["errors"] += 1

        # Set in memory cache
        try:
            # For memory cache, we need to handle TTL differently
            self.memory_cache[cache_key] = value
            success = True
            logger.debug(f"Cache set (Memory): {key}")
        except Exception as e:
            logger.error(f"Memory cache set error for key {key}: {e}")
            self.stats["errors"] += 1

        return success

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        cache_key = self._generate_cache_key(key)
        success = False

        # Delete from Redis
        if self.redis_enabled and self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
                success = True
                logger.debug(f"Cache delete (Redis): {key}")
            except Exception as e:
                logger.error(f"Redis delete error for key {key}: {e}")
                self.stats["errors"] += 1

        # Delete from memory cache
        try:
            self.memory_cache.pop(cache_key, None)
            success = True
            logger.debug(f"Cache delete (Memory): {key}")
        except Exception as e:
            logger.error(f"Memory cache delete error for key {key}: {e}")
            self.stats["errors"] += 1

        return success

    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        count = 0

        # Clear from Redis
        if self.redis_enabled and self.redis_client:
            try:
                cache_pattern = self._generate_cache_key(pattern + "*")
                keys = await self.redis_client.keys(cache_pattern)
                if keys:
                    count += await self.redis_client.delete(*keys)
                logger.debug(f"Cleared {count} Redis keys matching pattern: {pattern}")
            except Exception as e:
                logger.error(f"Redis pattern clear error for pattern {pattern}: {e}")
                self.stats["errors"] += 1

        # Clear from memory cache (simple implementation)
        try:
            cache_pattern = self._generate_cache_key(pattern)
            keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(cache_pattern)]
            for key in keys_to_delete:
                self.memory_cache.pop(key, None)
            count += len(keys_to_delete)
            logger.debug(f"Cleared {len(keys_to_delete)} memory keys matching pattern: {pattern}")
        except Exception as e:
            logger.error(f"Memory cache pattern clear error for pattern {pattern}: {e}")
            self.stats["errors"] += 1

        return count

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "redis_enabled": self.redis_enabled,
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_maxsize": self.memory_cache.maxsize
        }

    async def health_check(self) -> dict:
        """Perform cache health check"""
        health = {
            "memory_cache": "healthy",
            "redis_cache": "disabled"
        }

        # Check Redis
        if self.redis_enabled and self.redis_client:
            try:
                await self.redis_client.ping()
                health["redis_cache"] = "healthy"
            except Exception as e:
                health["redis_cache"] = f"unhealthy: {str(e)}"
                logger.error(f"Redis health check failed: {e}")

        return health


# Global cache manager instance
cache_manager = CacheManager()


# Convenience functions for backward compatibility
async def init_cache():
    """Initialize cache system"""
    await cache_manager.init_redis()


async def close_cache():
    """Close cache system"""
    await cache_manager.close_redis()


def get_from_cache(key: str, default: Any = None) -> Any:
    """Synchronous wrapper for cache get (for backward compatibility)"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(cache_manager.get(key, default))
    except RuntimeError:
        # If no event loop is running, use memory cache only
        cache_key = cache_manager._generate_cache_key(key)
        return cache_manager.memory_cache.get(cache_key, default)


def set_to_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Synchronous wrapper for cache set (for backward compatibility)"""
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(cache_manager.set(key, value, ttl))
    except RuntimeError:
        # If no event loop is running, use memory cache only
        try:
            cache_key = cache_manager._generate_cache_key(key)
            cache_manager.memory_cache[cache_key] = value
            return True
        except Exception:
            return False


# Async versions for new code
async def get_cache(key: str, default: Any = None) -> Any:
    """Get value from cache (async)"""
    return await cache_manager.get(key, default)


async def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Set value in cache (async)"""
    return await cache_manager.set(key, value, ttl)


async def delete_cache(key: str) -> bool:
    """Delete value from cache (async)"""
    return await cache_manager.delete(key)


async def clear_cache_pattern(pattern: str) -> int:
    """Clear cache entries matching pattern (async)"""
    return await cache_manager.clear_pattern(pattern)
