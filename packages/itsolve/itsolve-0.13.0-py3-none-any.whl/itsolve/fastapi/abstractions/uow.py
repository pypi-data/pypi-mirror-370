from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import (
    AsyncContextManager,
    Protocol,
    Self,
)

from pydantic.dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class IUOW(Protocol):
    def start(self) -> AsyncContextManager[Self]: ...


@dataclass
class UOW(ABC, IUOW):
    """
    Example of a unit of work implementation.

    ```python
    class IUOWExample(IUOW, Protocol):
        repo1: IRepo1
        repo2: IRepo2

    @dataclass
    class UOWExample(UOW, IUOWExample):
        repo1: IRepo1
        repo2: IRepo2

        async def _init_repos(self, session: AsyncSession):
            self.repo1 = Repo1(session)
            self.repo2 = Repo2(session)
    ```
    """

    async_session_factory: async_sessionmaker[AsyncSession]

    @asynccontextmanager
    async def start(self):
        async with self.async_session_factory.begin() as transaction:
            await self._init_repos(transaction)
            yield self

    @abstractmethod
    async def _init_repos(self, session: AsyncSession): ...
