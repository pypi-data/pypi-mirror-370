from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class SQLQuery(ABC):
    """
    Example:

    ```python
    class UpdateProductQuery(SQLQuery):
        product_id: int
        name: str

        async def load(
            self, *args: Any, **kwargs: Any
        ) -> None:
            await self.transaction.execute(...)
            await self.transaction.flush()

    async with async_session_factory.begin() as tx:
        q = UpdateProductQuery(tx).load()
    ```
    """

    transaction: AsyncSession = field(init=True)

    @abstractmethod
    async def load(self, *args: Any, **kwargs: Any) -> Any: ...
