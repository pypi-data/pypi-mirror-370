from pydantic import Field
from pydantic_settings import (
    SettingsConfigDict,
)

from .yml_settings import YmlSettings


class ServerSettings(YmlSettings):
    model_config = SettingsConfigDict(
        yaml_file="config.yml",
        yaml_config_section="server",
        yaml_file_encoding="utf-8",
    )
    host: str = Field(default="0.0.0.0", description="Host for server")
    port: int = Field(default=8000, description="Port for server")
    reload: bool = Field(default=True, description="Reload server")
    workers: int = Field(default=1, description="Workers for server")
    root_path: str = Field(default="", description="Root path for server")
    root_path_in_servers: bool = Field(
        default=True, description="Root path in servers"
    )
    prefix: str = Field(default="", description="Prefix for server")
    allow_origins: str = Field(
        default='["*"]', description="Allow hostnames for requests"
    )
    allow_credentials: bool = Field(
        default=True, description="Allow credentials for requests"
    )
    allow_methods: str = Field(
        default='["*"]', description="Allow methods for requests"
    )
    allow_headers: str = Field(
        default='["*"]', description="Allow headers for requests"
    )
