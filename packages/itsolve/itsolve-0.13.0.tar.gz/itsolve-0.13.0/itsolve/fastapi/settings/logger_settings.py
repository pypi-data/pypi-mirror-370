from typing import Literal

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .yml_settings import YmlSettings

LOG_LEVEL_TYPE = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "TRACE"]


class LoggerSettings(YmlSettings):
    model_config = SettingsConfigDict(
        yaml_file="config.yml",
        yaml_config_section="logger",
        yaml_file_encoding="utf-8",
    )
    console: bool = Field(default=True, description="Whether to log to console")
    console_level: LOG_LEVEL_TYPE = Field(
        default="INFO", description="Console log level"
    )
    console_time_format: str = Field(
        default="YYYY-MM-DD HH:mm:ss.SSS",
        description="Console log time format",
    )
    file: bool = Field(default=True, description="Whether to log to file")
    file_level: LOG_LEVEL_TYPE = Field(default="TRACE", description="File log level")
    file_rotation: str = Field(default="1 month", description="File log rotation")
    file_compression: str = Field(default="zip", description="File log compression")
    file_dir: str = Field(default="logs", description="File log directory")
    file_time_format: str = Field(
        default="ddd-DD HH:mm:ss.SSS", description="File log time format"
    )
    file_name: str = Field(
        default="{time:YYYY-MMM-DD}.log", description="File log name"
    )
    ctx_width: int = Field(default=50, description="Context width")
    ctx_indent: int = Field(default=2, description="Context indent")
    ctx_underscore_numbers: bool = Field(
        default=True, description="Context underscore numbers"
    )
    ctx_compact: bool = Field(default=True, description="Context compact")
    ctx_depth: int = Field(default=3, description="Context depth")

    loki_url: str = Field(
        default="http://localhost:3100/loki/api/v1/push", description="Loki URL"
    )
