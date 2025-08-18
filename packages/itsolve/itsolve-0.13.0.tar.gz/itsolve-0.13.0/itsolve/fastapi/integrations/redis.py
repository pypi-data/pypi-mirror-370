import contextlib
import inspect
from typing import Any, AsyncIterator

from loguru import logger
from redis import asyncio as aioredis
from redis.asyncio.client import Pipeline

from itsolve.fastapi.settings import RedisSettings


class RedisClient:
    def __init__(self, settings: RedisSettings) -> None:
        self.settings = settings
        logger.info(
            f"Initializing Redis client: redis://{settings.HOST}:{settings.PORT}/{settings.DB}",
            ctx={
                "max_connections": self.settings.MAX_CONNECTIONS,
                "encoding": self.settings.ENCODING,
                "db": self.settings.DB,
            },
        )
        self.pool = aioredis.ConnectionPool.from_url(
            f"redis://{settings.HOST}:{settings.PORT}/{settings.DB}",
            password=settings.PASSWORD or "redis_password",
            max_connections=settings.MAX_CONNECTIONS or 10,
            **{
                "encoding": "utf-8",
                "decode_responses": True,
            }
            if settings.ENCODING
            else {},
        )
        self.redis = aioredis.Redis(connection_pool=self.pool)
        logger.info("Redis client initialized")

    async def hset(
        self, pipe: Pipeline | None = None, *args: Any, **kwargs: Any
    ) -> int:
        """
        Wrapper for using redis hset to avoid Awaitable type errors.

        Args:
            pipe (Pipeline | None):
                The pipeline to use for the hset operation.
                If None, the operation will be performed
                directly on the redis client.
            *args: Positional arguments to pass to the hset method.
            **kwargs: Keyword arguments to pass to the hset method.

        Returns:
            int: The number of fields that were added.
        """
        response = (
            pipe.hset(*args, **kwargs) if pipe else self.redis.hset(*args, **kwargs)
        )
        if inspect.isawaitable(response):
            response = await response
        return response

    @contextlib.asynccontextmanager
    async def connection(
        self, *, throw_exception: bool = False
    ) -> AsyncIterator[aioredis.Redis]:
        """
        Asynchronous context manager for managing a Redis connection.

        ## Example Usage

        ```python
        async with (
            redis.connection() as client
        ):
            await (
                client.set(
                    "key",
                    "value",
                )
            )
            value = await client.get(
                "key"
            )
            print(value)
        ```

        ### Args:
            `throw_exception` (bool):
                If True, any exception
                raised during the session will be re-raised.

        Yields:
            AsyncIterator[aioredis.Redis]:
                An asynchronous iterator yielding a Redis client instance.
        """
        async with self.redis.client() as client:
            logger.info("Redis session started")
            try:
                yield client
            except Exception as e:
                logger.error(f"Redis session error: {e}")
                if throw_exception:
                    raise
            finally:
                await client.close()
                logger.info("Redis session ended")
