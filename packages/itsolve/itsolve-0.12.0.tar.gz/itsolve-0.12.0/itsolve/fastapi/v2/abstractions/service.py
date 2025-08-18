from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class Service(ABC):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.__session_factory = session_factory
