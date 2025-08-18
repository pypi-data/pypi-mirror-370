from sqlalchemy.orm import Mapped

from itsolve.fastapi.integrations.db.column_types import intpk


class IDMixin:
    id: Mapped[intpk]
