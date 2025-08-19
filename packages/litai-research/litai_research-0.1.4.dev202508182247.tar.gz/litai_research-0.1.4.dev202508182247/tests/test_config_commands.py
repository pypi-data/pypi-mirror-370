"""Tests for configuration commands."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from rich.console import Console

from litai.commands.config import handle_config_command, validate_model_name
from litai.config import Config


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def config(temp_dir):
    """Create a test config with temporary directory."""
    return Config(base_dir=temp_dir)


@pytest.fixture
def console():
    """Create a test console."""
    from rich.theme import Theme

    # Create a minimal theme for testing that includes the necessary styles
    test_theme = Theme(
        {
            "primary": "blue",
            "secondary": "purple",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "info": "cyan",
            "accent": "bright_green",
            "number": "bright_red",
            "dim_text": "dim",
            "heading": "bold blue",
            "command": "blue",
        },
    )

    return Console(file=open("/dev/null", "w"), theme=test_theme)


class TestConfigCommands:
    """Test configuration command handling."""

    def test_config_show_no_file(self, config, console):
        """Test config show when no config file exists."""
        with patch("litai.commands.config.console", console):
            # Just verify it doesn't crash when no config exists
            handle_config_command("show", config)

    def test_config_show_with_file(self, config, console):
        """Test config show when config file exists."""
        # Create a config file
        config_data = {
            "llm": {
                "provider": "openai",
                "small_model": "gpt-5-nano",
                "large_model": "gpt-5",
            },
            "editor": {"vi_mode": True},
            "tool_approval": False,
        }
        config.save_config(config_data)

        with patch("litai.commands.config.console", console):
            handle_config_command("show", config)

    def test_config_set_small_model(self, config, console):
        """Test setting small model via config command."""
        with patch("litai.commands.config.console", console):
            handle_config_command("set llm.small_model gpt-5-nano", config)

        assert config.get_small_model() == "gpt-5-nano"

    def test_config_set_large_model(self, config, console):
        """Test setting large model via config command."""
        with patch("litai.commands.config.console", console):
            handle_config_command("set llm.large_model gpt-5", config)

        assert config.get_large_model() == "gpt-5"

    def test_config_set_provider(self, config, console):
        """Test setting provider via config command."""
        with patch("litai.commands.config.console", console):
            handle_config_command("set llm.provider openai", config)

        config_data = config.load_config()
        assert config_data["llm"]["provider"] == "openai"

    def test_config_set_invalid_provider(self, config, console):
        """Test setting invalid provider."""
        with patch("litai.commands.config.console", console):
            handle_config_command("set llm.provider invalid", config)

        # Should not update config
        config_data = config.load_config()
        assert (
            "llm" not in config_data
            or config_data.get("llm", {}).get("provider") != "invalid"
        )

    def test_config_set_boolean_values(self, config, console):
        """Test setting boolean configuration values."""
        test_cases = [
            ("true", True),
            ("false", False),
            ("yes", True),
            ("no", False),
            ("1", True),
            ("0", False),
            ("on", True),
            ("off", False),
        ]

        with patch("litai.commands.config.console", console):
            for value_str, expected in test_cases:
                handle_config_command(f"set editor.vi_mode {value_str}", config)
                assert config.get_vi_mode() == expected

    def test_config_set_invalid_boolean(self, config, console):
        """Test setting invalid boolean value."""
        with patch("litai.commands.config.console", console):
            handle_config_command("set editor.vi_mode maybe", config)

        # Should not update config
        assert not config.get_vi_mode()  # Default value

    def test_config_set_invalid_key(self, config, console):
        """Test setting invalid configuration key."""
        with patch("litai.commands.config.console", console):
            handle_config_command("set invalid.key value", config)

        # Should not create invalid config
        config_data = config.load_config()
        assert "invalid" not in config_data

    def test_config_set_missing_args(self, config, console):
        """Test config set with missing arguments."""
        with patch("litai.commands.config.console", console):
            handle_config_command("set", config)
            handle_config_command("set llm.provider", config)

    def test_config_reset_small_model(self, config, console):
        """Test resetting small model to default."""
        # Set a custom value first
        config.set_small_model("custom-model")

        with patch("litai.commands.config.console", console):
            handle_config_command("reset llm.small_model", config)

        assert config.get_small_model() == "gpt-5-nano"

    def test_config_reset_large_model(self, config, console):
        """Test resetting large model to default."""
        # Set a custom value first
        config.set_large_model("custom-model")

        with patch("litai.commands.config.console", console):
            handle_config_command("reset llm.large_model", config)

        assert config.get_large_model() == "gpt-5"

    def test_config_reset_all(self, config, console):
        """Test resetting all configuration."""
        # Create some config first
        config.set_small_model("custom-model")
        config.update_config("editor.vi_mode", True)

        with (
            patch("litai.commands.config.console", console),
            patch("builtins.input", return_value="yes"),
        ):
            handle_config_command("reset", config)

        # Config file should be deleted
        assert not config.config_path.exists()

    def test_config_reset_all_cancelled(self, config, console):
        """Test cancelling reset all configuration."""
        # Create some config first
        config.set_small_model("custom-model")

        with (
            patch("litai.commands.config.console", console),
            patch("builtins.input", return_value="no"),
        ):
            handle_config_command("reset", config)

        # Config file should still exist
        assert config.config_path.exists()
        assert config.get_small_model() == "custom-model"

    def test_config_help(self, config, console):
        """Test config help command."""
        with patch("litai.commands.config.console", console):
            handle_config_command("--help", config)

    def test_config_invalid_subcommand(self, config, console):
        """Test invalid config subcommand."""
        with patch("litai.commands.config.console", console):
            handle_config_command("invalid", config)


class TestModelValidation:
    """Test model name validation."""

    def test_validate_valid_model_names(self):
        """Test validation of valid model names."""
        valid_names = [
            "gpt-5",
            "gpt-5-nano",
            "claude-3-opus",
            "gemini-pro",
            "llama-70b",
            "model_name",
            "model.name",
            "Model123",
        ]

        for name in valid_names:
            assert validate_model_name(name), f"Should accept valid model name: {name}"

    def test_validate_invalid_model_names(self):
        """Test validation of invalid model names."""
        invalid_names = [
            "",
            "   ",
            None,
            "model with spaces",
            "model@name",
            "model#name",
            "a" * 101,  # Too long
        ]

        for name in invalid_names:
            assert not validate_model_name(name), (
                f"Should reject invalid model name: {name}"
            )
