"""Config Manager Module for Bear Utils."""

from collections.abc import Callable
from functools import cached_property
import os
from pathlib import Path
import tomllib
from typing import Any, ClassVar

from pydantic import BaseModel, ValidationError, field_validator


def nullable_string_validator(field_name: str) -> Callable[..., str | None]:
    """Create a validator that converts 'null' strings to None."""

    @field_validator(field_name)
    @classmethod
    def _validate(cls: object, v: str | None) -> str | None:  # noqa: ARG001
        if isinstance(v, str) and v.lower() in ("null", "none", ""):
            return None
        return v

    return _validate


class ConfigManager[ConfigType: BaseModel]:
    """A generic configuration manager with environment-based overrides."""

    _default_config_paths: ClassVar[list[Path]] = [Path("~/.config/"), Path("config/")]
    _default_config_files: ClassVar[list[str]] = ["default.toml", "{env}.toml", "local.toml"]

    @staticmethod
    def _create_default_config_paths(project_name: str, env: str, file_names: list[str] | None = None) -> list[Path]:
        """Create default configuration paths based on the project name."""
        file_names = file_names or ConfigManager._default_config_files

        expanded_files: list[str] = [
            file_name.format(env=env) if "{env}" in file_name else file_name for file_name in file_names
        ]
        return [
            path.expanduser().resolve() / project_name.lower() / file_name
            for path in ConfigManager._default_config_paths
            for file_name in expanded_files
        ]

    def __init__(
        self,
        config_model: type[ConfigType],
        program_name: str,
        config_paths: list[Path] | None = None,
        file_names: list[str] | None = None,
        env: str = "dev",
    ) -> None:
        """Initialize the ConfigManager with a Pydantic model and configuration path."""
        self._model: type[ConfigType] = config_model
        self._env: str = env
        self._program_name: str = program_name.upper().replace(" ", "_").replace("-", "_")
        self._config_paths: list[Path] = config_paths or self._create_default_config_paths(
            self._program_name,
            env,
            file_names,
        )
        self._config: ConfigType | None = None

    def _get_env_overrides(self) -> dict[str, Any]:
        """Convert environment variables to nested dictionary structure."""
        env_config: dict[str, Any] = {}

        prefix: str = f"{self._program_name}_"

        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            # Convert BEAR_UTILS_DATABASE_HOST to ['database', 'host']
            clean_key: str = key[len(prefix) :].lower()
            parts: list[str] = clean_key.split("_")

            current: dict[str, Any] = env_config
            for part in parts[:-1]:
                current = current.setdefault(part, {})

            final_value: Any = self._convert_env_value(value)
            current[parts[-1]] = final_value
        return env_config

    def _convert_env_value(self, value: str) -> Any:
        """Convert string environment variables to appropriate types."""
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        if value.isdigit():
            return int(value)

        try:
            if "." in value:
                return float(value)
        except ValueError:
            pass

        if "," in value:
            return [item.strip() for item in value.split(",")]

        return value

    def _load_toml_file(self, file_path: Path) -> dict[str, Any]:
        """Load a TOML file and return its contents."""
        try:
            with open(file_path, "rb") as f:
                return tomllib.load(f)
        except FileNotFoundError:
            return {}
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML syntax in {file_path}: {e}") from e

    def _get_relevant_config_files(self) -> list[Path]:
        """Get config files in loading order for current environment."""
        file_order: list[str] = self._default_config_files

        relevant_files: list[Path] = []
        for file_name in file_order:
            for path in [p for p in self._config_paths if p.name == file_name]:
                relevant_files.append(path)
        return relevant_files

    @cached_property
    def resolved_config_paths(self) -> list[Path]:
        """Get the actual config files that exist and will be loaded."""
        return [path for path in self._config_paths if path.exists()]

    @cached_property
    def config_sources(self) -> dict[str, Any]:
        """Get detailed information about config sources and their contribution."""
        sources: dict[str, Any] = {
            "files_loaded": [],
            "files_searched": list(self._config_paths),
            "env_vars_used": [],
            "final_merge_order": [],
        }

        for path in self._config_paths:
            if path.exists():
                data: dict[str, Any] = self._load_toml_file(path)
                if data:
                    sources["files_loaded"].append({"path": str(path), "keys": list(data.keys())})
                    sources["final_merge_order"].append(str(path))

        env_overrides: dict[str, Any] = self._get_env_overrides()
        if env_overrides:
            sources["env_vars_used"] = [key for key in os.environ if key.startswith(f"{self._program_name}_")]
            sources["final_merge_order"].append("environment_variables")

        return sources

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries."""
        result: dict[str, Any] = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    @cached_property
    def load(self) -> ConfigType:
        """Load configuration from files and environment variables."""
        config_data: dict[str, Any] = {}

        for config_file in self.resolved_config_paths:
            file_data: dict[str, Any] = self._load_toml_file(config_file)
            config_data = self._deep_merge(config_data, file_data)

        env_overrides: dict[str, Any] = self._get_env_overrides()
        config_data = self._deep_merge(config_data, env_overrides)

        try:
            return self._model.model_validate(config_data)
        except ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e}") from e

    @property
    def config(self) -> ConfigType:
        """Get the loaded configuration."""
        if self._config is None:
            self._config = self.load
        return self._config

    def reload(self) -> ConfigType:
        """Force reload the configuration."""
        if hasattr(self, "load"):
            delattr(self, "load")
        self._config = None
        return self.config

    def create_default_config(self) -> None:
        """Create a default config file with example values."""
        if not self._config_paths:
            return

        default_path: Path = self._config_paths[0]

        if default_path.exists():
            return

        default_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            default_instance: ConfigType = self._model()
            toml_content: str = self._model_to_toml(default_instance)
            default_path.write_text(toml_content)
        except Exception as e:
            print(f"Could not create default config at {default_path}: {e}")

    def _model_to_toml(self, instance: ConfigType) -> str:
        """Convert a Pydantic model to TOML format."""
        lines: list[str] = ["# Default configuration"]

        def _dict_to_toml(data: dict[str, Any], prefix: str = "") -> None:
            for key, value in data.items():
                full_key: str = f"{prefix}.{key}" if prefix else key

                if isinstance(value, dict):
                    lines.append(f"\n[{full_key}]")
                    for sub_key, sub_value in value.items():
                        lines.append(f"{sub_key} = {self._format_toml_value(sub_value)}")
                elif not prefix:
                    lines.append(f"{key} = {self._format_toml_value(value)}")

        _dict_to_toml(instance.model_dump())
        return "\n".join(lines)

    def _format_toml_value(self, value: Any) -> str:
        """Format a value for TOML output."""
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, list):
            formatted_items = [self._format_toml_value(item) for item in value]
            return f"[{', '.join(formatted_items)}]"
        if value is None:
            return '"null"'
        return str(value)

    def has_config[T](self, config_type: type[T]) -> bool:
        """Check if the current configuration has an attribute or nested class of the given type."""
        for attr in dir(self.config):
            if attr.startswith(("_", "model_")):
                continue
            if attr == config_type.__name__.lower():
                return True
            if isinstance(getattr(self.config, attr, None), config_type):
                return True
        return False

    def get_config[T](self, config_type: type[T]) -> T | None:
        """Get the configuration of the specified type if it exists."""
        for attr in dir(self.config):
            if attr.startswith(("_", "model_")):
                continue
            if attr == config_type.__name__.lower():
                return getattr(self.config, attr)
            if isinstance(getattr(self.config, attr, None), config_type):
                return getattr(self.config, attr)
        return None


if __name__ == "__main__":
    # Example usage and models
    class DatabaseConfig(BaseModel):
        """Configuration for an example database connection."""

        host: str = "localhost"
        port: int = 5432
        username: str = "app"
        password: str = "secret"  # noqa: S105 This is just an example
        database: str = "myapp"

    class LoggingConfig(BaseModel):
        """Configuration for an example logging setup."""

        level: str = "INFO"
        format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file: str | None = None

        _validate_file = nullable_string_validator("file")

    class AppConfig(BaseModel):
        """Example application configuration model."""

        database: DatabaseConfig = DatabaseConfig()
        logging: LoggingConfig = LoggingConfig()
        environment: str = "development"
        debug: bool = False
        api_key: str = "your-api-key-here"
        allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    def get_config_manager(env: str = "dev") -> ConfigManager[AppConfig]:
        """Get a configured ConfigManager instance."""
        return ConfigManager[AppConfig](
            config_model=AppConfig,
            program_name="_test_app",
            file_names=["default.toml", "development.toml", "local.toml"],
            env=env,
        )

    config_manager: ConfigManager[AppConfig] = get_config_manager("dev")
    config_manager.create_default_config()
    config: AppConfig = config_manager.config

    print(f"Database host: {config.database.host}")
    print(f"Database port: {config.database.port}")
    print(f"Debug mode: {config.debug}")
    print(f"Environment: {config.environment}")

    if config_manager.has_config(LoggingConfig):
        logging_config: LoggingConfig | None = config_manager.get_config(LoggingConfig)
        if logging_config is not None:
            print(f"Logging level: {logging_config.level}")

    # Test environment variable override
    # Set: APP_DATABASE_HOST=production-db.example.com
    # Set: APP_DEBUG=true
