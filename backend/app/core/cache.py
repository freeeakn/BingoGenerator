from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from typing import Optional
import os

class CacheManager:
    _redis: Optional[aioredis.Redis] = None

    @classmethod
    async def init_cache(cls):
        """Initialize Redis connection and FastAPI Cache"""
        redis_url = os.getenv("REDIS_URL", "redis://localhost")
        cls._redis = aioredis.from_url(
            redis_url,
            encoding="utf8",
            decode_responses=True
        )
        FastAPICache.init(RedisBackend(cls._redis), prefix="bingo-cache")

    @classmethod
    async def get_redis(cls) -> aioredis.Redis:
        """Get Redis connection"""
        if not cls._redis:
            await cls.init_cache()
        return cls._redis

    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._redis:
            await cls._redis.close() 