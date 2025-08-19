"""Centralized status and loading animation manager."""

import os
import sys
import threading
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import structlog
from rich.console import Console
from rich.status import Status

logger = structlog.get_logger(__name__)


class StatusManager:
    """Singleton manager for application status and loading animations.

    Provides:
    - Centralized loading animations with configurable spinner styles
    - Interruptible animations (pause/resume for prompts)
    - Context manager support for automatic cleanup
    - Thread-safe operations
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "StatusManager":
        """Ensure singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the status manager."""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            # Lazy initialization - console created only when needed
            self._console: Console | None = None
            self._current_status: Status | None = None
            self._current_message = ""
            self._spinner_style = "balloon"  # Default spinner
            self._is_paused = False
            self._pause_state: dict[str, Any] | None = None
            self._start_time: datetime | None = None
            self._is_tty = sys.stdout.isatty()  # Check if running in terminal
            self._refresh_rate = 12 if self._is_tty else 4  # Optimize refresh rate
            # Don't log during initialization to avoid output before logging is configured

    @property
    def console(self) -> Console:
        """Lazy-load console for better performance."""
        if self._console is None:
            # Force color support if we're in a TTY, disable if not
            self._console = Console(
                force_terminal=self._is_tty,
                no_color=not self._is_tty,
            )
        return self._console

    def configure(self, spinner_style: str | None = None) -> None:
        """Configure the status manager.

        Args:
            spinner_style: Name of the spinner style (e.g., "dots", "balloon", "line")
        """
        if spinner_style:
            self._spinner_style = spinner_style
            logger.debug("StatusManager configured", spinner_style=spinner_style)

    def start(self, message: str) -> None:
        """Start showing a loading animation with the given message.

        Args:
            message: The status message to display
        """
        # Skip animations in non-TTY environments (pipes, redirects, etc.)
        if not self._is_tty:
            # Just log in non-interactive mode
            logger.debug("Status (non-TTY)", message=message)
            self._current_message = message
            self._start_time = datetime.now()
            return

        if self._current_status:
            self.stop()

        self._current_message = message
        self._start_time = datetime.now()
        self._current_status = self.console.status(
            message,
            spinner=self._spinner_style,
            refresh_per_second=self._refresh_rate,  # Optimized refresh rate
        )
        self._current_status.start()
        logger.debug("Status started", message=message, spinner=self._spinner_style)

    def update(self, message: str) -> None:
        """Update the current status message.

        Args:
            message: The new status message
        """
        self._current_message = message

        # Skip updates in non-TTY environments
        if not self._is_tty:
            logger.debug("Status update (non-TTY)", message=message)
            return

        if self._current_status:
            self._current_status.update(message)
            logger.debug("Status updated", message=message)

    def stop(self) -> None:
        """Stop the current loading animation."""
        if self._start_time:
            duration = (datetime.now() - self._start_time).total_seconds()
            # Log performance warning if operation was slow
            if duration > 10:
                logger.warning(
                    "Slow operation detected",
                    message=self._current_message,
                    duration_seconds=duration,
                )
            else:
                logger.debug(
                    "Status stopped",
                    message=self._current_message,
                    duration_seconds=duration,
                )
        else:
            logger.debug("Status stopped", message=self._current_message)

        if self._current_status:
            self._current_status.stop()
            self._current_status = None

        self._current_message = ""
        self._start_time = None
        self._is_paused = False
        self._pause_state = None

    async def pause(self) -> None:
        """Pause the current animation (for interruptions like prompts).

        Saves the current state to restore after resume.
        """
        # No need to pause in non-TTY mode
        if not self._is_tty:
            return

        if self._current_status and not self._is_paused:
            self._pause_state = {
                "message": self._current_message,
                "spinner": self._spinner_style,
                "start_time": self._start_time,
            }
            self._current_status.stop()
            # Important: set to None so is_active() correctly returns False
            self._current_status = None
            self._is_paused = True
            logger.debug("Status paused", message=self._current_message)

    async def resume(self) -> None:
        """Resume a paused animation."""
        # No need to resume in non-TTY mode
        if not self._is_tty:
            return

        if self._is_paused and self._pause_state:
            self._current_status = self.console.status(
                self._pause_state["message"],
                spinner=self._pause_state["spinner"],
                refresh_per_second=self._refresh_rate,
            )
            self._current_status.start()
            self._current_message = self._pause_state["message"]
            self._start_time = self._pause_state["start_time"]
            self._is_paused = False
            logger.debug("Status resumed", message=self._current_message)

    @asynccontextmanager
    async def loading(self, message: str) -> AsyncGenerator["StatusManager", None]:
        """Context manager for loading animations.

        Args:
            message: The status message to display

        Example:
            async with status_manager.loading("Processing..."):
                await some_async_operation()
        """
        self.start(message)
        try:
            yield self
        finally:
            self.stop()

    def is_active(self) -> bool:
        """Check if a status animation is currently active."""
        return self._current_status is not None

    def is_paused(self) -> bool:
        """Check if the status animation is currently paused."""
        return self._is_paused

    def get_available_spinners(self) -> list[str]:
        """Get list of available spinner styles."""
        return [
            "dots",
            "dots2",
            "dots3",
            "dots4",
            "dots5",
            "dots6",
            "dots7",
            "dots8",
            "dots9",
            "dots10",
            "dots11",
            "dots12",
            "dots13",
            "line",
            "line2",
            "pipe",
            "simpleDots",
            "simpleDotsScrolling",
            "star",
            "star2",
            "flip",
            "hamburger",
            "growVertical",
            "growHorizontal",
            "balloon",
            "balloon2",
            "noise",
            "bounce",
            "boxBounce",
            "boxBounce2",
            "triangle",
            "arc",
            "circle",
            "squareCorners",
            "circleQuarters",
            "circleHalves",
            "squish",
            "toggle",
            "toggle2",
            "toggle3",
            "toggle4",
            "toggle5",
            "toggle6",
            "toggle7",
            "toggle8",
            "toggle9",
            "toggle10",
            "toggle11",
            "toggle12",
            "toggle13",
            "arrow",
            "arrow2",
            "arrow3",
            "bouncingBar",
            "bouncingBall",
            "smiley",
            "monkey",
            "hearts",
            "clock",
            "earth",
            "material",
            "moon",
            "runner",
            "pong",
            "shark",
            "dqpb",
            "weather",
            "christmas",
            "grenade",
            "point",
            "layer",
            "betaWave",
        ]

    def __repr__(self) -> str:
        """String representation of the StatusManager."""
        return f"StatusManager(active={self.is_active()}, paused={self.is_paused()}, spinner='{self._spinner_style}', tty={self._is_tty})"


# Global instance for easy access
_status_manager = StatusManager()


def get_status_manager() -> StatusManager:
    """Get the global StatusManager instance."""
    return _status_manager
