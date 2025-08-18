"""Tests for configuration management."""

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from litai.config import Config


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestConfig:
    """Test configuration management."""

    def test_default_base_dir(self) -> None:
        """Test that default base directory is ~/.litai."""
        config = Config()
        assert config.base_dir == Path.home() / ".litai"

    def test_custom_base_dir(self, temp_dir: Path) -> None:
        """Test using a custom base directory."""
        config = Config(base_dir=temp_dir)
        assert config.base_dir == temp_dir

    def test_directories_created(self, temp_dir: Path) -> None:
        """Test that all required directories are created."""
        config = Config(base_dir=temp_dir)

        # Check all directories exist
        assert config.base_dir.exists()
        assert config.pdfs_dir.exists()
        assert config.db_dir.exists()

        # Check they are directories
        assert config.base_dir.is_dir()
        assert config.pdfs_dir.is_dir()
        assert config.db_dir.is_dir()

    def test_pdfs_dir_path(self, temp_dir: Path) -> None:
        """Test PDFs directory path."""
        config = Config(base_dir=temp_dir)
        assert config.pdfs_dir == temp_dir / "pdfs"

    def test_db_dir_path(self, temp_dir: Path) -> None:
        """Test database directory path."""
        config = Config(base_dir=temp_dir)
        assert config.db_dir == temp_dir / "db"

    def test_db_path(self, temp_dir: Path) -> None:
        """Test database file path."""
        config = Config(base_dir=temp_dir)
        assert config.db_path == temp_dir / "db" / "litai.db"

    def test_pdf_path(self, temp_dir: Path) -> None:
        """Test PDF path generation."""
        config = Config(base_dir=temp_dir)

        paper_id = "test123"
        pdf_path = config.pdf_path(paper_id)

        assert pdf_path == temp_dir / "pdfs" / "test123.pdf"
        assert pdf_path.parent.exists()  # Directory should exist

    def test_config_path(self, temp_dir: Path) -> None:
        """Test configuration file path."""
        config = Config(base_dir=temp_dir)
        assert config.config_path == temp_dir / "config.json"

    def test_load_config_empty(self, temp_dir: Path) -> None:
        """Test loading config when file doesn't exist."""
        config = Config(base_dir=temp_dir)
        loaded = config.load_config()
        assert loaded == {}

    def test_save_and_load_config(self, temp_dir: Path) -> None:
        """Test saving and loading configuration."""
        config = Config(base_dir=temp_dir)

        test_config = {
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key_env": "MY_API_KEY",
            },
        }

        config.save_config(test_config)
        loaded = config.load_config()

        assert loaded == test_config
        assert config.config_path.exists()

    def test_update_config(self, temp_dir: Path) -> None:
        """Test updating configuration values."""
        config = Config(base_dir=temp_dir)

        # Set initial value
        config.update_config("llm.provider", "openai")
        loaded = config.load_config()
        assert loaded["llm"]["provider"] == "openai"

        # Update existing value
        config.update_config("llm.provider", "anthropic")
        loaded = config.load_config()
        assert loaded["llm"]["provider"] == "anthropic"

        # Add nested value
        config.update_config("llm.model", "claude-3")
        loaded = config.load_config()
        assert loaded["llm"]["model"] == "claude-3"
        assert loaded["llm"]["provider"] == "anthropic"

    def test_update_config_nested_creation(self, temp_dir: Path) -> None:
        """Test that update_config creates nested structures."""
        config = Config(base_dir=temp_dir)

        # Update deeply nested value on empty config
        config.update_config("app.features.enabled", True)
        loaded = config.load_config()

        assert loaded["app"]["features"]["enabled"] is True

    def test_get_vi_mode_default(self, temp_dir: Path) -> None:
        """Test get_vi_mode returns False by default."""
        config = Config(base_dir=temp_dir)
        assert config.get_vi_mode() is False

    def test_get_vi_mode_set_true(self, temp_dir: Path) -> None:
        """Test get_vi_mode returns True when set."""
        config = Config(base_dir=temp_dir)
        config.update_config("editor.vi_mode", True)
        assert config.get_vi_mode() is True

    def test_get_vi_mode_set_false(self, temp_dir: Path) -> None:
        """Test get_vi_mode returns False when explicitly set."""
        config = Config(base_dir=temp_dir)
        config.update_config("editor.vi_mode", False)
        assert config.get_vi_mode() is False

    def test_user_prompt_path(self, temp_dir: Path) -> None:
        """Test user prompt file path."""
        config = Config(base_dir=temp_dir)
        assert config.user_prompt_path == temp_dir / "user_prompt.txt"

    # Small/Large Model Tests

    def test_small_large_model_getters(self, temp_dir: Path) -> None:
        """Test that model getters work with new schema."""
        config = Config(base_dir=temp_dir)

        # Set up configuration with both small and large models
        test_config = {
            "llm": {
                "small_model": "gpt-5-mini",
                "large_model": "gpt-5-turbo",
                "provider": "openai",
            },
        }
        config.save_config(test_config)

        # Test that getters return the correct models
        assert config.get_small_model() == "gpt-5-mini"
        assert config.get_large_model() == "gpt-5-turbo"

    def test_models_without_config(self, temp_dir: Path) -> None:
        """Test that default models are returned when not configured."""
        config = Config(base_dir=temp_dir)

        # Without any configuration, should get defaults
        assert config.get_small_model() == "gpt-5-nano"
        assert config.get_large_model() == "gpt-5"

    def test_model_setters(self, temp_dir: Path) -> None:
        """Test setting small/large models independently."""
        config = Config(base_dir=temp_dir)

        # Set models using the new setters
        config.set_small_model("gpt-5-nano")
        config.set_large_model("gpt-5")

        # Verify they were set correctly
        assert config.get_small_model() == "gpt-5-nano"
        assert config.get_large_model() == "gpt-5"

        # Verify they're stored in the config file
        saved_config = config.load_config()
        assert saved_config["llm"]["small_model"] == "gpt-5-nano"
        assert saved_config["llm"]["large_model"] == "gpt-5"

    def test_default_values(self, temp_dir: Path) -> None:
        """Test default model values when not specified."""
        config = Config(base_dir=temp_dir)

        # With no configuration, should return defaults
        assert config.get_small_model() == "gpt-5-nano"
        assert config.get_large_model() == "gpt-5"

    def test_model_setter_validation(self, temp_dir: Path) -> None:
        """Test validation in model setters."""
        config = Config(base_dir=temp_dir)

        # Test empty string validation
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            config.set_small_model("")

        with pytest.raises(ValueError, match="Model name cannot be empty"):
            config.set_large_model("")

        # Test whitespace-only validation
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            config.set_small_model("   ")

        with pytest.raises(ValueError, match="Model name cannot be empty"):
            config.set_large_model("   ")

    def test_partial_configuration(self, temp_dir: Path) -> None:
        """Test when only one model is configured."""
        config = Config(base_dir=temp_dir)

        # Set up config where only small model is set
        test_config = {
            "llm": {
                "small_model": "gpt-5-nano",
                "provider": "openai",
            },
        }
        config.save_config(test_config)

        # Small model uses configured value, large model uses default
        assert config.get_small_model() == "gpt-5-nano"
        assert config.get_large_model() == "gpt-5"

    def test_model_whitespace_handling(self, temp_dir: Path) -> None:
        """Test that model setters handle whitespace correctly."""
        config = Config(base_dir=temp_dir)

        # Set models with leading/trailing whitespace
        config.set_small_model("  gpt-5-nano  ")
        config.set_large_model("  gpt-5  ")

        # Should be stripped
        assert config.get_small_model() == "gpt-5-nano"
        assert config.get_large_model() == "gpt-5"
