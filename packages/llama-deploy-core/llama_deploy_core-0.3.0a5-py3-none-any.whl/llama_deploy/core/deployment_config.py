from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ServiceSource(BaseModel):
    """Configuration for where to load the workflow or other source. Path is relative to the config file its declared within."""

    location: str

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "name" in data:
                data["location"] = data.pop("name")
        return data


class Service(BaseModel):
    """Configuration for a single service."""

    source: ServiceSource | None = Field(None)
    import_path: str | None = Field(None)
    env: dict[str, str] | None = Field(None)
    env_files: list[str] | None = Field(None)
    python_dependencies: list[str] | None = Field(None)

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Handle YAML aliases
            if "path" in data:
                data["import_path"] = data.pop("path")
            if "import-path" in data:
                data["import_path"] = data.pop("import-path")
            if "env-files" in data:
                data["env_files"] = data.pop("env-files")

        return data

    def module_location(self) -> tuple[str, str]:
        """
        Parses the import path, and target, discarding legacy file path portion, if any

        "src/module.workflow:my_workflow" -> ("module.workflow", "my_workflow")
        """
        if self.import_path is None:
            raise ValueError("import_path is required to compute module_location")
        module_name, workflow_name = self.import_path.split(":")
        return Path(module_name).name, workflow_name


class UIService(Service):
    port: int = Field(
        default=3000,
        description="The TCP port to use for the nextjs server",
    )


class DeploymentConfig(BaseModel):
    """Model definition mapping a deployment config file."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    name: str
    default_service: str | None = Field(None)
    services: dict[str, Service]
    ui: UIService | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_fields(cls, data: Any) -> Any:
        # Handle YAML aliases
        if isinstance(data, dict):
            if "default-service" in data:
                data["default_service"] = data.pop("default-service")

        return data

    @classmethod
    def from_yaml_bytes(cls, src: bytes) -> "DeploymentConfig":
        """Read config data from bytes containing yaml code."""
        config = yaml.safe_load(src) or {}
        return cls(**config)

    @classmethod
    def from_yaml(cls, path: Path, name: str | None = None) -> "DeploymentConfig":
        """Read config data from a yaml file."""
        with open(path, "r", encoding="utf-8") as yaml_file:
            config = yaml.safe_load(yaml_file) or {}

        instance = cls(**config)
        if name:
            instance.name = name
        return instance
