from datetime import datetime, timezone

from pydantic import Field


class TimestampMixin:
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), alias="createdAt"
    )
    updated_at: datetime | None = Field(default=None, alias="updatedAt")
