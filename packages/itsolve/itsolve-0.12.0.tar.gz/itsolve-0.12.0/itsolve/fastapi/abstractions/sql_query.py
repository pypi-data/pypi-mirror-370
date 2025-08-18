from abc import ABC, abstractmethod
from typing import Any
from pydantic.dataclasses import dataclass
from pydantic.fields import Field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import UpdateBase


@dataclass
class SQLQuery[ReturnType](ABC):
    """
    Example:

    ```python
    class UpdateProductQuery(SQLQuery[None]):
        product_id: int
        query: UpdateBase = Field(init=False)
        name: str

        def __post_init__(self):
            self.query = update(table).where(ORM.id == self.product_id).values(name=self.name)

        async def load(
            self, session: AsyncSession, *args: Any, **kwargs: Any
        ) -> None:
            await session.execute(self.query)
            await session.commit()
    ```
    """

    query: UpdateBase = Field(init=False)

    @abstractmethod
    async def load(
        self, session: AsyncSession, *args: Any, **kwargs: Any
    ) -> ReturnType: ...
