from fastapi import Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from typing import Callable, Optional
from .cache import CacheManager
from .exceptions import BingoException, ErrorCode

class RateLimitManager:
    @classmethod
    async def init_limiter(cls):
        """Initialize rate limiter with Redis"""
        redis = await CacheManager.get_redis()
        await FastAPILimiter.init(redis)

    @staticmethod
    def limit_requests(
        times: int = 10,
        seconds: Optional[int] = None,
        minutes: Optional[int] = None,
        hours: Optional[int] = None
    ) -> Callable:
        """Rate limit decorator with custom time windows"""
        if hours:
            seconds = hours * 3600
        elif minutes:
            seconds = minutes * 60
        elif not seconds:
            seconds = 60  # Default: 1 minute

        return RateLimiter(times=times, seconds=seconds)

    @staticmethod
    async def check_ip_ban(request: Request):
        """Check if IP is banned due to too many failed attempts"""
        redis = await CacheManager.get_redis()
        client_ip = request.client.host
        
        # Check if IP is banned
        is_banned = await redis.get(f"ip_ban:{client_ip}")
        if is_banned:
            raise BingoException(
                code=ErrorCode.INVALID_CREDENTIALS,
                message="Too many failed attempts. Please try again later.",
                status_code=429
            )

    @staticmethod
    async def record_failed_attempt(request: Request):
        """Record failed login attempt"""
        redis = await CacheManager.get_redis()
        client_ip = request.client.host
        
        # Increment failed attempts counter
        key = f"failed_attempts:{client_ip}"
        attempts = await redis.incr(key)
        await redis.expire(key, 3600)  # Expire in 1 hour
        
        # Ban IP if too many failed attempts
        if attempts >= 5:
            await redis.setex(f"ip_ban:{client_ip}", 3600, "1")  # Ban for 1 hour

# Example usage:
# @router.post("/login")
# @RateLimitManager.limit_requests(times=5, minutes=15)
# async def login(request: Request):
#     await RateLimitManager.check_ip_ban(request)
#     # ... login logic ... 