from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DATABASE__", env_file_encoding="utf-8"
    )
    HOST: str = Field(
        default="localhost",
        description="Database host",
    )
    PORT: int = Field(
        default=5432,
        description="Database port",
    )
    USER: str = Field(
        default="postgres",
        description="Database user",
    )
    PASSWORD: str = Field(
        default="postgres",
        description="Database password",
    )
    NAME: str = Field(
        default="db",
        description="Database name",
    )
    LOG_ORM: bool = Field(
        default=False,
        description="Log ORM queries",
    )
    POOL_SIZE: int = Field(default=10, description="Database pool size")
    MAX_OVERFLOW: int = Field(default=5, description="Database max overflow")

    @property
    def URL(self) -> str:  # noqa: N802
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"
