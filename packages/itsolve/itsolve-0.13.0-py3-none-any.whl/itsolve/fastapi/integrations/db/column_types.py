from datetime import datetime, timezone
from typing import Annotated, TypeVar

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

T = TypeVar("T")

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True, unique=True)]
required = Annotated[T, mapped_column(nullable=False)]
timestamp = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        default=lambda: datetime.now(timezone.utc),
    ),
]
updated_timestamp = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        onupdate=func.current_timestamp(),
    ),
]
