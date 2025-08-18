from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .pyproject_settings import PyprojectSettings


class ProjectSettings(PyprojectSettings):
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("project",), extra="ignore"
    )
    name: str = Field(default="project_name", description="Project name")
    version: str = Field(default="0.1.0", description="Project version")
    description: str = Field(default="", description="Project description")
