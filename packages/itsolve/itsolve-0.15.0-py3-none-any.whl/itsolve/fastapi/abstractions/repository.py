from typing import (
    TypeVar,
    Protocol,
    Any,
)
from pydantic.dataclasses import dataclass

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

Entity = TypeVar("Entity")


class IRepository[Entity](Protocol):
    async def add(self, *args: Any, **kwargs: Any) -> Entity: ...

    async def get(self, *args: Any, **kwargs: Any) -> Entity: ...

    async def update(self, *args: Any, **kwargs: Any) -> Entity: ...

    async def delete(self, *args: Any, **kwargs: Any) -> None: ...


@dataclass
class BaseSQLRepository:
    table: type[DeclarativeBase]


@dataclass
class SQLRepository(BaseSQLRepository):
    session: AsyncSession


@dataclass
class SQLIndependentRepository(BaseSQLRepository):
    async_session_factory: async_sessionmaker[AsyncSession]
