from pydantic import BaseModel, Field


class DefaultTUserPayload(BaseModel):
    id: str = Field(default="0", alias="sub")
