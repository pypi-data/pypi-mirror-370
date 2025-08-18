# ruff: noqa: ARG003
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)


class PermissionsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="PERMISSIONS__",
        yaml_file="config.yml",
        yaml_config_section="permissions",
        yaml_file_encoding="utf-8",
    )
    file_model_name: str = Field(default="permissions_model.conf")
    file_policy_name: str = Field(default="policy.csv")
    RESOURCE_URL: str = Field(default="http://localhost:8004/permissions")
    mock_policy: bool = Field(default=True)
    enabled: bool = Field(default=True)

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
