"""Editor configuration and management for LitAI."""

import shutil
import subprocess
from pathlib import Path
from typing import Any

from structlog import get_logger

logger = get_logger(__name__)

EDITOR_CONFIGS: dict[str, dict[str, str | list[str]]] = {
    # GUI editors
    "vscode": {"command": "code", "args": ["--wait"], "type": "gui"},
    "code": {"command": "code", "args": ["--wait"], "type": "gui"},
    "cursor": {"command": "cursor", "args": ["--wait"], "type": "gui"},
    "sublime": {"command": "subl", "args": ["--wait"], "type": "gui"},
    "atom": {"command": "atom", "args": ["--wait"], "type": "gui"},
    "brackets": {"command": "brackets", "args": [], "type": "gui"},
    "gedit": {"command": "gedit", "args": [], "type": "gui"},
    "kate": {"command": "kate", "args": [], "type": "gui"},
    "geany": {"command": "geany", "args": [], "type": "gui"},
    "notepadplusplus": {"command": "notepad++", "args": [], "type": "gui"},
    # Terminal editors
    "vim": {"command": "vim", "args": [], "type": "terminal"},
    "nvim": {"command": "nvim", "args": [], "type": "terminal"},
    "emacs": {"command": "emacs", "args": [], "type": "terminal"},
    "nano": {"command": "nano", "args": [], "type": "terminal"},
    "micro": {"command": "micro", "args": [], "type": "terminal"},
    "joe": {"command": "joe", "args": [], "type": "terminal"},
    "mcedit": {"command": "mcedit", "args": [], "type": "terminal"},
    "ne": {"command": "ne", "args": [], "type": "terminal"},
    "tilde": {"command": "tilde", "args": [], "type": "terminal"},
    # macOS specific
    "bbedit": {"command": "bbedit", "args": ["--wait"], "type": "gui"},
    "coderunner": {"command": "coderunner", "args": [], "type": "gui"},
    "coteditor": {"command": "cot", "args": ["--wait"], "type": "gui"},
    "macvim": {"command": "mvim", "args": [], "type": "gui"},
    "nova": {"command": "nova", "args": ["--wait"], "type": "gui"},
    "slickedit": {"command": "vs", "args": [], "type": "gui"},
    "subethaedit": {"command": "see", "args": ["--wait"], "type": "gui"},
    "textmate": {"command": "mate", "args": ["--wait"], "type": "gui"},
    "textwrangler": {"command": "edit", "args": ["--wait"], "type": "gui"},
    # IDE editors
    "pycharm": {"command": "pycharm", "args": ["--wait"], "type": "gui"},
    "idea": {"command": "idea", "args": ["--wait"], "type": "gui"},
    "webstorm": {"command": "webstorm", "args": ["--wait"], "type": "gui"},
    "rubymine": {"command": "rubymine", "args": ["--wait"], "type": "gui"},
    "goland": {"command": "goland", "args": ["--wait"], "type": "gui"},
    "phpstorm": {"command": "phpstorm", "args": ["--wait"], "type": "gui"},
    "clion": {"command": "clion", "args": ["--wait"], "type": "gui"},
    "rider": {"command": "rider", "args": ["--wait"], "type": "gui"},
    "datagrip": {"command": "datagrip", "args": ["--wait"], "type": "gui"},
    "androidstudio": {"command": "studio", "args": ["--wait"], "type": "gui"},
    "fleet": {"command": "fleet", "args": ["--wait"], "type": "gui"},
}


def detect_available_editors() -> list[str]:
    """Detect which configured editors are available on the system.

    Returns:
        List of editor names that are available on the system
    """
    available = []
    for name, config in EDITOR_CONFIGS.items():
        command = config["command"]
        assert isinstance(command, str)  # Help mypy understand type
        if shutil.which(command):
            available.append(name)

    logger.info("editors_detected", available=available)
    return available


def get_default_editor() -> str:
    """Get the first available editor from a priority list.

    Returns:
        Name of the first available editor, or 'nano' as ultimate fallback
    """
    # Priority order: GUI editors first, then terminal editors, then fallbacks
    priority_list = [
        "vscode",
        "code",
        "cursor",
        "sublime",
        "atom",  # Popular GUI editors
        "vim",
        "nvim",
        "emacs",
        "nano",
        "micro",  # Popular terminal editors
        "vi",  # System fallback
    ]

    available_editors = detect_available_editors()

    # Find first available editor from priority list
    for editor in priority_list:
        if editor in available_editors:
            logger.info("default_editor_selected", editor=editor)
            return editor

    # Ultimate fallback - check for vi which should exist on most Unix systems
    if shutil.which("vi"):
        logger.info("default_editor_selected", editor="vi")
        return "vi"

    # If nothing else works, return nano as fallback
    logger.warning("no_editor_found_using_fallback", fallback="nano")
    return "nano"


def validate_editor(editor_name: str) -> bool:
    """Validate that an editor is supported and available.

    Args:
        editor_name: Name of the editor to validate

    Returns:
        True if editor is supported and available, False otherwise
    """
    if editor_name not in EDITOR_CONFIGS:
        logger.warning("editor_not_supported", editor=editor_name)
        return False

    command = EDITOR_CONFIGS[editor_name]["command"]
    assert isinstance(command, str)  # Help mypy understand type
    if not shutil.which(command):
        logger.warning("editor_not_available", editor=editor_name, command=command)
        return False

    return True


def open_in_editor(file_path: Path, config: Any) -> tuple[bool, str]:
    """Open a file in the configured editor.

    Args:
        file_path: Path to the file to open
        config: Configuration object with get_editor() method

    Returns:
        Tuple of (success, error_message). Error message is empty on success.
    """
    try:
        # Check if file exists
        if not file_path.exists():
            error_msg = f"File does not exist: {file_path}"
            logger.error("file_not_found", file_path=str(file_path))
            return False, error_msg

        # Get configured editor
        editor_name = config.get_editor()
        logger.info(
            "opening_file_in_editor", file_path=str(file_path), editor=editor_name,
        )

        # Build command based on editor configuration
        if editor_name in EDITOR_CONFIGS:
            # Use predefined configuration
            editor_config = EDITOR_CONFIGS[editor_name]
            command = editor_config["command"]
            args = editor_config["args"]
            assert isinstance(command, str)  # Help mypy understand type
            assert isinstance(args, list)  # Help mypy understand type

            # Check if editor command is available
            if not shutil.which(command):
                error_msg = f"Editor command not found: {command}"
                logger.error(
                    "editor_command_not_found", command=command, editor=editor_name,
                )
                return False, error_msg

            # Build full command with arguments and file path
            full_command = [command] + args + [str(file_path)]
        else:
            # Fallback to raw command for custom editors
            if not shutil.which(editor_name):
                error_msg = f"Custom editor command not found: {editor_name}"
                logger.error("custom_editor_not_found", editor=editor_name)
                return False, error_msg

            full_command = [editor_name, str(file_path)]

        # Execute the editor command
        logger.info("executing_editor_command", command=full_command)
        result = subprocess.run(full_command, check=True)

        logger.info(
            "editor_executed_successfully",
            file_path=str(file_path),
            editor=editor_name,
            return_code=result.returncode,
        )
        return True, ""

    except subprocess.CalledProcessError as e:
        error_msg = f"Editor process failed with exit code {e.returncode}"
        logger.error(
            "editor_process_failed",
            file_path=str(file_path),
            editor=editor_name,
            exit_code=e.returncode,
            error=str(e),
        )
        return False, error_msg

    except FileNotFoundError as e:
        error_msg = f"File or command not found: {e}"
        logger.error(
            "file_or_command_not_found", file_path=str(file_path), error=str(e),
        )
        return False, error_msg

    except Exception as e:
        error_msg = f"Unexpected error opening editor: {e}"
        logger.error("unexpected_editor_error", file_path=str(file_path), error=str(e))
        return False, error_msg


def open_in_editor_with_fallback(file_path: Path, config: Any) -> tuple[bool, str]:
    """Open a file in editor with fallback to system editors if configured editor fails.

    Args:
        file_path: Path to the file to open
        config: Configuration object with get_editor() method

    Returns:
        Tuple of (success, error_message). Error message is empty on success.
    """
    # Try configured editor first
    success, error = open_in_editor(file_path, config)
    if success:
        return True, ""

    # Log warning about configured editor failure
    configured_editor = config.get_editor()
    logger.warning(
        "configured_editor_failed_trying_fallbacks",
        editor=configured_editor,
        error=error,
    )

    # Try fallback editors in priority order
    fallback_editors = ["nano", "vi"]

    for fallback in fallback_editors:
        if shutil.which(fallback):
            logger.info("trying_fallback_editor", fallback=fallback)

            try:
                # Execute fallback editor directly
                full_command = [fallback, str(file_path)]
                result = subprocess.run(full_command, check=True)

                logger.info(
                    "fallback_editor_executed_successfully",
                    file_path=str(file_path),
                    fallback=fallback,
                    return_code=result.returncode,
                )
                return True, ""

            except subprocess.CalledProcessError as e:
                logger.warning(
                    "fallback_editor_failed",
                    fallback=fallback,
                    exit_code=e.returncode,
                    error=str(e),
                )
                continue

            except Exception as e:
                logger.warning(
                    "fallback_editor_unexpected_error", fallback=fallback, error=str(e),
                )
                continue
        else:
            logger.debug("fallback_editor_not_available", fallback=fallback)

    # No working editor found
    error_msg = f"No working editor found. Configured editor '{configured_editor}' failed: {error}. Fallback editors (nano, vi) also unavailable or failed."
    logger.error(
        "no_working_editor_found",
        configured_editor=configured_editor,
        original_error=error,
    )
    return False, error_msg
