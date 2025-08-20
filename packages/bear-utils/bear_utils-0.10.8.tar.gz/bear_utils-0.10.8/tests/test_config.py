import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest
from pydantic import BaseModel

from bear_utils.config.config_manager import ConfigManager, nullable_string_validator


class MockDatabaseConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str = "app"


class MockLoggingConfig(BaseModel):
    level: str = "INFO"
    file: str | None = None
    _validate_file = nullable_string_validator("file")


class MockAppConfig(BaseModel):
    database: MockDatabaseConfig = MockDatabaseConfig()
    logging: MockLoggingConfig = MockLoggingConfig()
    debug: bool = False


class TestConfigManager:
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """Create a ConfigManager with temporary paths."""
        config_paths = [temp_config_dir / "default.toml"]
        manager = ConfigManager[MockAppConfig](
            config_model=MockAppConfig, program_name="TEST_APP", config_paths=config_paths, env="test"
        )

        if hasattr(manager, "load"):
            delattr(manager, "load")
        manager._config = None
        return manager

    def test_env_vars(self):
        """Debug environment variable processing."""
        with patch.dict(os.environ, {"TEST_APP_DATABASE_HOST": "env.db", "TEST_APP_DEBUG": "true"}):
            config_manager = ConfigManager[MockAppConfig](
                config_model=MockAppConfig, program_name="TEST_APP", config_paths=[], env="test"
            )

            print(f"Program name: {config_manager._program_name}")
            print(f"Env overrides: {config_manager._get_env_overrides()}")

            config = config_manager.config
            print(f"Final config: {config.model_dump()}")

    def test_loads_default_config_when_no_files_exist(self, config_manager):
        """Test that default values are used when no config files exist."""
        config = config_manager.config

        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.debug is False

    def test_loads_toml_file_config(self, temp_config_dir):
        """Test loading configuration from TOML file."""
        config_file = temp_config_dir / "default.toml"

        config_file.write_text("""
        debug = true

        [database]
        host = "production.db"
        port = 3306
        """)

        assert config_file.exists()

        config_manager = ConfigManager[MockAppConfig](
            config_model=MockAppConfig, program_name="TEST_APP", config_paths=[config_file], env="test"
        )

        config = config_manager.config
        assert config.database.host == "production.db"
        assert config.debug is True

    def test_environment_variable_overrides(self, temp_config_dir):
        with patch.dict(os.environ, {"TEST_APP_DATABASE_HOST": "env.db", "TEST_APP_DEBUG": "true"}):
            config_manager = ConfigManager[MockAppConfig](
                config_model=MockAppConfig,
                program_name="test_app",
                config_paths=[],
                env="test",
            )

            print(f"Env overrides: {config_manager._get_env_overrides()}")

            config = config_manager.config
            assert config.database.host == "env.db"

    def test_env_value_conversion(self, config_manager):
        """Test environment variable type conversion."""
        with patch.dict(os.environ, {"TEST_APP_DATABASE_PORT": "9999", "TEST_APP_DEBUG": "false"}):
            config = config_manager.config

            assert config.database.port == 9999
            assert isinstance(config.database.port, int)
            assert config.debug is False
            assert isinstance(config.debug, bool)

    def test_has_config_method(self, config_manager):
        """Test the has_config method."""
        assert config_manager.has_config(MockDatabaseConfig) is True
        assert config_manager.has_config(MockLoggingConfig) is True

        class NonExistentConfig(BaseModel):
            pass

        assert config_manager.has_config(NonExistentConfig) is False

    def test_get_config_method(self, config_manager):
        """Test the get_config method returns correct types."""
        db_config = config_manager.get_config(MockDatabaseConfig)
        assert isinstance(db_config, MockDatabaseConfig)
        assert db_config.host == "localhost"

        logging_config = config_manager.get_config(MockLoggingConfig)
        assert isinstance(logging_config, MockLoggingConfig)
        assert logging_config.level == "INFO"

    def test_config_reload(self, temp_config_dir):
        """Test that reload picks up config changes."""
        config_file = temp_config_dir / "default.toml"
        config_file.write_text("debug = false")

        config_manager = ConfigManager[MockAppConfig](
            config_model=MockAppConfig, program_name="test_app", config_paths=[config_file], env="test"
        )
        initial_config: MockAppConfig = config_manager.config
        assert initial_config.debug is False
        config_file.write_text("debug = true")
        reloaded_config: MockAppConfig = config_manager.reload()
        assert reloaded_config.debug is True

    def test_nullable_string_validator(self) -> None:
        """Test the nullable string validator."""

        class TestModel(BaseModel):
            optional_field: str | None = None
            _validate_field = nullable_string_validator("optional_field")

        # Test null conversion
        model1 = TestModel(optional_field="null")
        assert model1.optional_field is None

        model2 = TestModel(optional_field="none")
        assert model2.optional_field is None

        model3 = TestModel(optional_field="")
        assert model3.optional_field is None

        # Test regular string
        model4 = TestModel(optional_field="actual_value")
        assert model4.optional_field == "actual_value"

    def test_deep_merge_functionality(self, config_manager):
        """Test that deep merge works correctly."""
        base = {"a": {"b": 1, "c": 2}, "d": 3}
        override = {"a": {"b": 99}, "e": 4}

        result = config_manager._deep_merge(base, override)

        assert result["a"]["b"] == 99  # Overridden
        assert result["a"]["c"] == 2  # Preserved
        assert result["d"] == 3  # Preserved
        assert result["e"] == 4  # Added

    def test_config_sources_tracking(self, temp_config_dir, config_manager):
        """Test that config sources are properly tracked."""
        config_file = temp_config_dir / "default.toml"
        config_file.write_text('[database]\nhost = "test"')

        sources = config_manager.config_sources

        assert len(sources["files_loaded"]) == 1
        assert "default.toml" in sources["files_loaded"][0]["path"]
        assert "database" in sources["files_loaded"][0]["keys"]
