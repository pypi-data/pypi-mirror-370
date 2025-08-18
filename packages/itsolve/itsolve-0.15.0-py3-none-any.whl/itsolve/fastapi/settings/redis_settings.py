from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="REDIS__", env_file_encoding="utf-8"
    )
    HOST: str = Field(default="localhost", description="Redis host")
    PORT: int = Field(default=6379, description="Redis port")
    PASSWORD: str | None = Field(default=None, description="Redis password")
    DB: int = Field(default=0, description="Redis database")
    MAX_CONNECTIONS: int = Field(
        default=10, description="Maximum number of connections"
    )
    ENCODING: bool = Field(default=False, description="Redis encoding")
