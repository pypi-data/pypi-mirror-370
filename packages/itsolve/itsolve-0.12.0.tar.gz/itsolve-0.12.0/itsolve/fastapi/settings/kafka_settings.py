from pydantic import Field
from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    ENABLED: bool = Field(default=False)
    TOPICS: str = Field(default="")
    HOST: str = Field(default="localhost")
    PORT: int = Field(default=29092)

    @property
    def URL(self) -> str:  # noqa: N802
        return f"{self.HOST}:{self.PORT}"
