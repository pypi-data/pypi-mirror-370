"""Configuration and directory management for LitAI."""

import json
import os
from pathlib import Path
from typing import Any

from litai.utils.logger import get_logger

logger = get_logger(__name__)


class Config:
    """Manages LitAI configuration and directory structure."""

    def __init__(self, base_dir: Path | None = None):
        """Initialize config with base directory.

        Args:
            base_dir: Base directory for LitAI data. Defaults to ~/.litai
        """
        if base_dir is None:
            base_dir = Path.home() / ".litai"
        self.base_dir = Path(base_dir)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        directories = [
            self.base_dir,
            self.pdfs_dir,
            self.db_dir,
        ]

        for dir_path in directories:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info("Created directory", path=str(dir_path))

    @property
    def pdfs_dir(self) -> Path:
        """Directory for storing downloaded PDFs."""
        return self.base_dir / "pdfs"

    @property
    def db_dir(self) -> Path:
        """Directory for database files."""
        return self.base_dir / "db"

    @property
    def db_path(self) -> Path:
        """Path to the SQLite database file."""
        return self.db_dir / "litai.db"

    def pdf_path(self, paper_id: str) -> Path:
        """Get the path for a specific paper's PDF.

        Args:
            paper_id: Unique identifier for the paper

        Returns:
            Path where the PDF should be stored
        """
        return self.pdfs_dir / f"{paper_id}.pdf"

    @property
    def config_path(self) -> Path:
        """Path to the configuration file."""
        return self.base_dir / "config.json"

    @property
    def user_prompt_path(self) -> Path:
        """Path to user prompt file."""
        return self.base_dir / "user_prompt.txt"

    @property
    def data_dir(self) -> Path:
        """Directory for application data files like token usage tracking."""
        return self.base_dir

    def load_config(self) -> dict[str, Any]:
        """Load configuration from file.

        Returns:
            Configuration dict or empty dict if file doesn't exist
        """
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path) as f:
                config = json.load(f)
                logger.info("Loaded configuration", path=str(self.config_path))
                return dict(config)
        except (OSError, json.JSONDecodeError) as e:
            logger.error(
                "Failed to load config",
                path=str(self.config_path),
                error=str(e),
            )
            return {}

    def save_config(self, config: dict[str, Any]) -> None:
        """Save configuration to file.

        Args:
            config: Configuration dictionary to save
        """
        try:
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            logger.info("Saved configuration", path=str(self.config_path))
        except OSError as e:
            logger.error(
                "Failed to save config",
                path=str(self.config_path),
                error=str(e),
            )
            raise

    def update_config(self, key_path: str, value: Any) -> None:
        """Update a specific configuration value.

        Args:
            key_path: Dot-separated path to config key (e.g., "llm.provider")
            value: Value to set
        """
        config = self.load_config()

        # Navigate through the key path, creating dicts as needed
        keys = key_path.split(".")
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the final value
        current[keys[-1]] = value

        self.save_config(config)

    def get_vi_mode(self) -> bool:
        """Get vi mode setting from configuration.

        Returns:
            True if vi mode is enabled, False otherwise (default)
        """
        config = self.load_config()
        editor_config = config.get("editor", {})
        return bool(editor_config.get("vi_mode", False))

    def get_editor(self) -> str:
        """Get editor configuration with priority order.

        Checks in priority order:
        1. Config file setting
        2. LITAI_EDITOR environment variable
        3. EDITOR environment variable
        4. Default from editor module

        Returns:
            The editor name
        """
        from .editor import get_default_editor

        config = self.load_config()
        editor_config = config.get("editor", {})

        # 1. Check config file setting
        if "editor" in editor_config and editor_config["editor"]:
            return str(editor_config["editor"]).strip()

        # 2. Check LITAI_EDITOR environment variable
        litai_editor = os.environ.get("LITAI_EDITOR")
        if litai_editor:
            return litai_editor.strip()

        # 3. Check EDITOR environment variable
        system_editor = os.environ.get("EDITOR")
        if system_editor:
            return system_editor.strip()

        # 4. Default from editor module
        return get_default_editor()

    def set_editor(self, editor: str) -> None:
        """Set editor configuration.

        Args:
            editor: The editor name to set

        Raises:
            ValueError: If editor name is empty or invalid
        """
        from .editor import validate_editor

        if not editor or not editor.strip():
            raise ValueError("Editor name cannot be empty")

        editor = editor.strip()

        # Validate the editor
        if not validate_editor(editor):
            raise ValueError(
                f"Editor '{editor}' is not supported or not available on this system",
            )

        self.update_config("editor.editor", editor)
        logger.info("Editor updated", editor=editor)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation.

        Args:
            key: Config key in dot notation (e.g., 'synthesis.tool_approval')
            default: Default value if key not found

        Returns:
            Config value or default
        """
        config = self.load_config()
        parts = key.split(".")
        value: Any = config
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set a config value using dot notation.

        Args:
            key: Config key in dot notation (e.g., 'synthesis.tool_approval')
            value: Value to set
        """
        config = self.load_config()
        parts = key.split(".")

        # Navigate to the parent dict
        current = config
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the value
        current[parts[-1]] = value
        self.save_config(config)
        logger.info(f"Config updated: {key} = {value}")

    def get_list_columns(self) -> list[str]:
        """Get configured columns for /list command.

        Returns default columns if not configured.
        """
        config = self.load_config()
        columns_str = config.get("display", {}).get("list_columns", "")

        if not columns_str:
            # Default columns
            return [
                "no",
                "title",
                "authors",
                "year",
                "citations",
                "notes",
                "tags",
                "venue",
            ]

        return [col.strip().lower() for col in columns_str.split(",")]

    # Small/Large Model Configuration Support

    def get_small_model(self) -> str:
        """Get the small model configuration.

        Returns the configured small_model or the default.

        Returns:
            The small model name
        """
        config = self.load_config()
        llm_config = config.get("llm", {})

        # Check for small_model
        if "small_model" in llm_config and llm_config["small_model"]:
            return str(llm_config["small_model"])

        # Default small model
        return "gpt-5-nano"

    def get_large_model(self) -> str:
        """Get the large model configuration.

        Returns the configured large_model or the default.

        Returns:
            The large model name
        """
        config = self.load_config()
        llm_config = config.get("llm", {})

        # Check for large_model
        if "large_model" in llm_config and llm_config["large_model"]:
            return str(llm_config["large_model"])

        # Default large model
        return "gpt-5"

    def set_small_model(self, model: str) -> None:
        """Set the small model configuration.

        Args:
            model: The small model name to set
        """
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")

        self.update_config("llm.small_model", model.strip())
        logger.info("Small model updated", model=model.strip())

    def set_large_model(self, model: str) -> None:
        """Set the large model configuration.

        Args:
            model: The large model name to set
        """
        if not model or not model.strip():
            raise ValueError("Model name cannot be empty")

        self.update_config("llm.large_model", model.strip())
        logger.info("Large model updated", model=model.strip())

    def get_spinner_style(self) -> str:
        """Get the spinner style configuration.

        Returns:
            The configured spinner style or 'balloon' as default
        """
        config = self.load_config()
        ui_config = config.get("ui", {})
        return str(ui_config.get("spinner_style", "balloon"))

    def set_spinner_style(self, style: str) -> None:
        """Set the spinner style configuration.

        Args:
            style: The spinner style to set (e.g., "dots", "balloon", "line")
        """
        if not style or not style.strip():
            raise ValueError("Spinner style cannot be empty")

        self.update_config("ui.spinner_style", style.strip())
        logger.info("Spinner style updated", style=style.strip())
