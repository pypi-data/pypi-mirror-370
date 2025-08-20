"""Tests for editor configuration and management."""

import os
import shutil
import subprocess
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from litai.config import Config
from litai.editor import (
    EDITOR_CONFIGS,
    detect_available_editors,
    get_default_editor,
    open_in_editor,
    open_in_editor_with_fallback,
    validate_editor,
)


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_file(temp_dir: Path) -> Path:
    """Create a test file for editor operations."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("Test content\n")
    return test_file


@pytest.fixture
def config(temp_dir: Path) -> Config:
    """Create a Config instance for testing."""
    return Config(base_dir=temp_dir)


class TestEditorDetection:
    """Test editor detection functionality."""

    def test_detect_available_editors_none_available(self) -> None:
        """Test detection when no editors are available."""
        with patch("shutil.which", return_value=None):
            available = detect_available_editors()
            assert available == []

    def test_detect_available_editors_some_available(self) -> None:
        """Test detection when some editors are available."""

        def mock_which(command: str) -> str | None:
            if command in ["vim", "code"]:
                return f"/usr/bin/{command}"
            return None

        with patch("shutil.which", side_effect=mock_which):
            available = detect_available_editors()
            assert "vim" in available
            assert "vscode" in available  # vscode uses "code" command
            assert "nano" not in available

    def test_detect_available_editors_all_available(self) -> None:
        """Test detection when all editors are available."""
        with patch("shutil.which", return_value="/usr/bin/mock"):
            available = detect_available_editors()
            # Should include all configured editors
            assert len(available) == len(EDITOR_CONFIGS)
            assert all(editor in EDITOR_CONFIGS for editor in available)


class TestEditorConfiguration:
    """Test editor configuration functionality."""

    def test_get_editor_priority_config_file(self, config: Config) -> None:
        """Test that config file setting has highest priority."""
        # Set editor in config file
        config.update_config("editor.editor", "vim")

        # Mock environment variables
        with patch.dict(os.environ, {"LITAI_EDITOR": "nano", "EDITOR": "emacs"}):
            # Mock that vim is available
            with patch("shutil.which", return_value="/usr/bin/vim"):
                editor = config.get_editor()
                assert editor == "vim"

    def test_get_editor_priority_litai_editor_env(self, config: Config) -> None:
        """Test that LITAI_EDITOR env var has second priority."""
        # Mock environment variables
        with patch.dict(os.environ, {"LITAI_EDITOR": "nano", "EDITOR": "emacs"}):
            # Mock that nano is available but vim is not
            with patch("shutil.which", return_value="/usr/bin/nano"):
                editor = config.get_editor()
                assert editor == "nano"

    def test_get_editor_priority_editor_env(self, config: Config) -> None:
        """Test that EDITOR env var has third priority."""
        # Mock environment variable
        with patch.dict(os.environ, {"EDITOR": "emacs"}, clear=True):
            # Mock that emacs is available
            with patch("shutil.which", return_value="/usr/bin/emacs"):
                editor = config.get_editor()
                assert editor == "emacs"

    def test_get_editor_priority_default(self, config: Config) -> None:
        """Test fallback to default editor."""
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            # Mock get_default_editor to return a specific value
            with patch("litai.editor.get_default_editor", return_value="nano"):
                editor = config.get_editor()
                assert editor == "nano"

    def test_get_editor_strips_whitespace(self, config: Config) -> None:
        """Test that editor names are stripped of whitespace."""
        # Set editor with whitespace in config
        config.update_config("editor.editor", "  vim  ")

        editor = config.get_editor()
        assert editor == "vim"  # Should be stripped

    def test_set_editor_valid(self, config: Config) -> None:
        """Test setting a valid editor."""
        with patch("litai.editor.validate_editor", return_value=True):
            config.set_editor("vim")

            # Check that it was saved
            saved_config = config.load_config()
            assert saved_config["editor"]["editor"] == "vim"

    def test_set_editor_empty_string(self, config: Config) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Editor name cannot be empty"):
            config.set_editor("")

    def test_set_editor_whitespace_only(self, config: Config) -> None:
        """Test that whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Editor name cannot be empty"):
            config.set_editor("   ")

    def test_set_editor_invalid(self, config: Config) -> None:
        """Test that invalid editor raises ValueError."""
        with patch("litai.editor.validate_editor", return_value=False):
            with pytest.raises(
                ValueError, match="Editor 'invalid' is not supported or not available",
            ):
                config.set_editor("invalid")

    def test_set_editor_strips_whitespace(self, config: Config) -> None:
        """Test that set_editor strips whitespace."""
        with patch("litai.editor.validate_editor", return_value=True):
            config.set_editor("  vim  ")

            # Check that it was saved without whitespace
            saved_config = config.load_config()
            assert saved_config["editor"]["editor"] == "vim"


class TestEditorValidation:
    """Test editor validation functionality."""

    def test_validate_editor_supported_and_available(self) -> None:
        """Test validation of supported and available editor."""
        with patch("shutil.which", return_value="/usr/bin/vim"):
            assert validate_editor("vim") is True

    def test_validate_editor_not_supported(self) -> None:
        """Test validation of unsupported editor."""
        assert validate_editor("nonexistent-editor") is False

    def test_validate_editor_supported_but_not_available(self) -> None:
        """Test validation of supported but unavailable editor."""
        with patch("shutil.which", return_value=None):
            assert validate_editor("vim") is False


class TestDefaultEditor:
    """Test default editor selection."""

    def test_get_default_editor_vscode_available(self) -> None:
        """Test that vscode is preferred when available."""

        def mock_which(command: str) -> str | None:
            if command == "code":
                return "/usr/bin/code"
            return None

        with patch("shutil.which", side_effect=mock_which):
            editor = get_default_editor()
            assert editor == "vscode"

    def test_get_default_editor_vim_fallback(self) -> None:
        """Test fallback to vim when GUI editors aren't available."""

        def mock_which(command: str) -> str | None:
            if command == "vim":
                return "/usr/bin/vim"
            return None

        with patch("shutil.which", side_effect=mock_which):
            editor = get_default_editor()
            assert editor == "vim"

    def test_get_default_editor_vi_fallback(self) -> None:
        """Test fallback to vi when configured editors aren't available."""

        def mock_which(command: str) -> str | None:
            # Only vi is available, not in EDITOR_CONFIGS
            if command == "vi":
                return "/usr/bin/vi"
            return None

        with patch("shutil.which", side_effect=mock_which):
            editor = get_default_editor()
            assert editor == "vi"

    def test_get_default_editor_ultimate_fallback(self) -> None:
        """Test ultimate fallback to nano when nothing is available."""
        with patch("shutil.which", return_value=None):
            editor = get_default_editor()
            assert editor == "nano"


class TestEditorOpening:
    """Test opening files in editors."""

    def test_open_in_editor_success(self, test_file: Path, config: Config) -> None:
        """Test successfully opening a file in editor."""
        # Configure vim as editor
        config.update_config("editor.editor", "vim")

        # Mock successful subprocess run
        mock_result = Mock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with patch("shutil.which", return_value="/usr/bin/vim"):
                success, error = open_in_editor(test_file, config)

                assert success is True
                assert error == ""
                mock_run.assert_called_once_with(["vim", str(test_file)], check=True)

    def test_open_in_editor_file_not_exists(
        self, temp_dir: Path, config: Config,
    ) -> None:
        """Test opening non-existent file."""
        nonexistent_file = temp_dir / "nonexistent.txt"

        success, error = open_in_editor(nonexistent_file, config)

        assert success is False
        assert "File does not exist" in error

    def test_open_in_editor_command_not_found(
        self, test_file: Path, config: Config,
    ) -> None:
        """Test opening file when editor command not found."""
        config.update_config("editor.editor", "vim")

        with patch("shutil.which", return_value=None):
            success, error = open_in_editor(test_file, config)

            assert success is False
            assert "Editor command not found" in error

    def test_open_in_editor_subprocess_error(
        self, test_file: Path, config: Config,
    ) -> None:
        """Test handling subprocess errors."""
        config.update_config("editor.editor", "vim")

        with patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, ["vim"]),
        ):
            with patch("shutil.which", return_value="/usr/bin/vim"):
                success, error = open_in_editor(test_file, config)

                assert success is False
                assert "Editor process failed" in error

    def test_open_in_editor_with_args(self, test_file: Path, config: Config) -> None:
        """Test opening file with editor that has arguments."""
        config.update_config("editor.editor", "vscode")

        mock_result = Mock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with patch("shutil.which", return_value="/usr/bin/code"):
                success, error = open_in_editor(test_file, config)

                assert success is True
                assert error == ""
                # Should include --wait argument from vscode config
                mock_run.assert_called_once_with(
                    ["code", "--wait", str(test_file)], check=True,
                )

    def test_open_in_editor_custom_editor(
        self, test_file: Path, config: Config,
    ) -> None:
        """Test opening file with custom editor not in EDITOR_CONFIGS."""
        config.update_config("editor.editor", "custom-editor")

        mock_result = Mock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with patch("shutil.which", return_value="/usr/bin/custom-editor"):
                success, error = open_in_editor(test_file, config)

                assert success is True
                assert error == ""
                # Should use raw command without additional args
                mock_run.assert_called_once_with(
                    ["custom-editor", str(test_file)], check=True,
                )

    def test_open_in_editor_custom_editor_not_found(
        self, test_file: Path, config: Config,
    ) -> None:
        """Test opening file with unavailable custom editor."""
        config.update_config("editor.editor", "custom-editor")

        with patch("shutil.which", return_value=None):
            success, error = open_in_editor(test_file, config)

            assert success is False
            assert "Custom editor command not found" in error


class TestEditorFallback:
    """Test editor fallback functionality."""

    def test_open_in_editor_with_fallback_success(
        self, test_file: Path, config: Config,
    ) -> None:
        """Test successful opening without needing fallback."""
        config.update_config("editor.editor", "vim")

        mock_result = Mock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result):
            with patch("shutil.which", return_value="/usr/bin/vim"):
                success, error = open_in_editor_with_fallback(test_file, config)

                assert success is True
                assert error == ""

    def test_open_in_editor_with_fallback_nano(
        self, test_file: Path, config: Config,
    ) -> None:
        """Test fallback to nano when configured editor fails."""
        config.update_config("editor.editor", "broken-editor")

        # Mock nano as available
        def mock_which(command: str) -> str | None:
            if command == "nano":
                return "/usr/bin/nano"
            return None

        mock_result = Mock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with patch("shutil.which", side_effect=mock_which):
                success, error = open_in_editor_with_fallback(test_file, config)

                assert success is True
                assert error == ""
                # Should have called nano as fallback
                mock_run.assert_called_with(["nano", str(test_file)], check=True)

    def test_open_in_editor_with_fallback_vi(
        self, test_file: Path, config: Config,
    ) -> None:
        """Test fallback to vi when nano is not available."""
        config.update_config("editor.editor", "broken-editor")

        # Mock only vi as available
        def mock_which(command: str) -> str | None:
            if command == "vi":
                return "/usr/bin/vi"
            return None

        mock_result = Mock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            with patch("shutil.which", side_effect=mock_which):
                success, error = open_in_editor_with_fallback(test_file, config)

                assert success is True
                assert error == ""
                # Should have called vi as fallback
                mock_run.assert_called_with(["vi", str(test_file)], check=True)

    def test_open_in_editor_with_fallback_all_fail(
        self, test_file: Path, config: Config,
    ) -> None:
        """Test when all editors fail."""
        config.update_config("editor.editor", "broken-editor")

        # No editors available
        with patch("shutil.which", return_value=None):
            success, error = open_in_editor_with_fallback(test_file, config)

            assert success is False
            assert "No working editor found" in error

    def test_open_in_editor_with_fallback_nano_fails(
        self, test_file: Path, config: Config,
    ) -> None:
        """Test when nano is available but fails to execute."""
        config.update_config("editor.editor", "broken-editor")

        # Mock nano as available but vi as unavailable
        def mock_which(command: str) -> str | None:
            if command == "nano":
                return "/usr/bin/nano"
            if command == "vi":
                return "/usr/bin/vi"
            return None

        def mock_run(command: list[str], **kwargs):
            if "nano" in command:
                raise subprocess.CalledProcessError(1, command)
            # vi succeeds
            mock_result = Mock()
            mock_result.returncode = 0
            return mock_result

        with patch("subprocess.run", side_effect=mock_run) as mock_run_patch:
            with patch("shutil.which", side_effect=mock_which):
                success, error = open_in_editor_with_fallback(test_file, config)

                assert success is True
                assert error == ""
                # Should have tried nano first, then vi
                calls = mock_run_patch.call_args_list
                assert len(calls) == 2
                assert "nano" in str(calls[0])
                assert "vi" in str(calls[1])
