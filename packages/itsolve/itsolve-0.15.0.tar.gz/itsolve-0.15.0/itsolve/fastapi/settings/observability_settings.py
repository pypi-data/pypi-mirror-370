from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ObservabilitySettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OBSERVABILITY__",
        yaml_file_encoding="utf-8",
    )
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = Field(default=None)

    @property
    def enabled(self) -> bool:
        return bool(self.OTEL_EXPORTER_OTLP_ENDPOINT)
