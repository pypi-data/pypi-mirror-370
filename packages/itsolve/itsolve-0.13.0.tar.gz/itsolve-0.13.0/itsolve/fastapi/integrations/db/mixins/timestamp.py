from sqlalchemy.orm import Mapped

from itsolve.fastapi.integrations.db.column_types import (
    timestamp,
    updated_timestamp,
)


class TimestampMixin:
    created_at: Mapped[timestamp]
    updated_at: Mapped[updated_timestamp]
