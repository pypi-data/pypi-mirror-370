from __future__ import annotations

import contextlib
import os
from typing import TYPE_CHECKING, AsyncIterator

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import CreateSchema, DropSchema

from itsolve.fastapi.settings import DatabaseSettings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


class Database:
    def __init__(self, settings: DatabaseSettings) -> None:
        self._settings = settings
        self._engine: AsyncEngine = create_async_engine(
            settings.URL,
            echo=settings.LOG_ORM,
            pool_size=settings.POOL_SIZE,
            max_overflow=settings.MAX_OVERFLOW,
        )
        self._session_factory = async_sessionmaker(
            self._engine, expire_on_commit=False, class_=AsyncSession
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @contextlib.asynccontextmanager
    async def async_session_factory(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as session:
            try:
                yield session
            except Exception:
                logger.debug("Session rollback because of exception")
                await session.rollback()
                raise
            finally:
                await session.close()


class TestDatabase(Database):
    @contextlib.asynccontextmanager
    async def async_session_factory(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as session:
            mode = os.environ.get("MODE", "production")
            if mode == "test":
                pytest_xdist_worker = os.environ.get("PYTEST_XDIST_WORKER", None)
                if pytest_xdist_worker:
                    await session.execute(
                        text(f"SET search_path TO test_{pytest_xdist_worker}")
                    )
            try:
                yield session
            except Exception as e:
                logger.debug("Session rollback because of exception")
                logger.debug(f"Exception details: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()

    @contextlib.asynccontextmanager
    async def schema_lifespan(self, schema_name: str) -> AsyncIterator[None]:
        async with self._engine.begin() as conn:
            await conn.execute(CreateSchema(schema_name, if_not_exists=True))
            await conn.execute(text(f"SET search_path TO {schema_name}"))
        yield
        async with self._engine.begin() as conn:
            await conn.execute(DropSchema(schema_name, cascade=True, if_exists=True))

    @contextlib.asynccontextmanager
    async def lifespan_database(
        self, Base: type[DeclarativeBase]
    ) -> AsyncIterator[None]:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
