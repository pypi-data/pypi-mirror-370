# ruff: noqa: ARG003
from collections.abc import Sequence

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class JwtSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="JWT__",
        yaml_file="config.yml",
        yaml_config_section="jwt",
        yaml_file_encoding="utf-8",
    )
    mock_user: bool = Field(
        default=False, description="Mock user for JWT authentication"
    )
    access_token_lifetime: int = Field(
        default=15, description="Expiration access token in minutes"
    )
    refresh_token_lifetime: int = Field(
        default=30, description="Expiration refresh token in days"
    )
    SIGNING_KEY: str = Field(
        default="secret", description="Secret key of sign of jwt"
    )
    audience: Sequence[str] = Field(default=["aud"], description="Audience")
    issuer: str = Field(default="iss", description="Issuer")
    prefix_header: str | None = Field(
        default="Bearer", description="Prefix header for jwt"
    )
    max_active_sessions: int | None = Field(
        default=5, description="Max active login user's sessions"
    )
    algorithm: str = Field(default="HS256", description="Algorithm for jwt")
    token_location: list[str] = Field(
        default=["headers", "query", "cookies", "json"],
        description="Location of jwt token",
    )
    header_name: str = Field(
        default="Authorization", description="Header name for jwt"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            YamlConfigSettingsSource(settings_cls),
            EnvSettingsSource(settings_cls),
        )
