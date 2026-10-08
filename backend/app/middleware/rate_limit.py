from fastapi import Request
from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
    ):
        super().__init__(app)

        self.requests_per_minute = requests_per_minute
        self.redis = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        client_ip = request.client.host
        redis_key = f"rate_limit:{client_ip}"

        try:
            current_count = await self.redis.incr(redis_key)

            if current_count == 1:
                await self.redis.expire(redis_key, 60)

            if current_count > self.requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Please try again later."
                    },
                )

        except (RedisError, TimeoutError, OSError):
            # Redis is unavailable.
            # Fail open so the application remains usable.
            pass

        response = await call_next(request)

        return response