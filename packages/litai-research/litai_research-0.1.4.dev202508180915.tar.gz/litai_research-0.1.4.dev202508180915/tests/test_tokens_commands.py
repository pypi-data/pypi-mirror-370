"""Tests for token usage commands."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from rich.console import Console

from litai.commands.tokens import (
    format_number,
    format_session_summary_compact,
    handle_tokens_command,
)
from litai.config import Config
from litai.token_tracker import TokenTracker, TokenUsage


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
def token_tracker(config):
    """Create a test token tracker."""
    return TokenTracker(config)


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


class TestTokensCommands:
    """Test token usage command handling."""

    def test_tokens_command_no_tracker(self, config, console):
        """Test tokens command when no tracker is available."""
        with patch("litai.commands.tokens.console", console):
            handle_tokens_command("", config, None)

    def test_tokens_session_empty(self, config, token_tracker, console):
        """Test tokens session command with no usage."""
        with patch("litai.commands.tokens.console", console):
            handle_tokens_command("session", config, token_tracker)

    def test_tokens_session_with_usage(self, config, token_tracker, console):
        """Test tokens session command with usage data."""
        # Add some mock usage
        token_tracker.track_usage(
            TokenUsage(
                input_tokens=100,
                output_tokens=50,
                model="gpt-5-nano",
                model_size="small",
                operation_type="search",
            ),
        )

        token_tracker.track_usage(
            TokenUsage(
                input_tokens=500,
                output_tokens=200,
                model="gpt-5",
                model_size="large",
                operation_type="synthesis",
            ),
        )

        with patch("litai.commands.tokens.console", console):
            handle_tokens_command("session", config, token_tracker)

    def test_tokens_all_empty(self, config, token_tracker, console):
        """Test tokens all command with no usage."""
        with patch("litai.commands.tokens.console", console):
            handle_tokens_command("all", config, token_tracker)

    def test_tokens_all_with_usage(self, config, token_tracker, console):
        """Test tokens all command with usage data."""
        # Add some mock usage
        token_tracker.track_usage(
            TokenUsage(
                input_tokens=1000,
                output_tokens=500,
                model="gpt-5-nano",
                model_size="small",
            ),
        )

        with patch("litai.commands.tokens.console", console):
            handle_tokens_command("all", config, token_tracker)

    def test_tokens_help(self, config, token_tracker, console):
        """Test tokens help command."""
        with patch("litai.commands.tokens.console", console):
            handle_tokens_command("--help", config, token_tracker)

    def test_tokens_invalid_subcommand(self, config, token_tracker, console):
        """Test invalid tokens subcommand."""
        with patch("litai.commands.tokens.console", console):
            handle_tokens_command("invalid", config, token_tracker)

    def test_tokens_tips_now_invalid(self, config, token_tracker, console):
        """Test that tips subcommand is now invalid."""
        with patch("litai.commands.tokens.console", console):
            handle_tokens_command("tips", config, token_tracker)

    def test_tokens_default_subcommand(self, config, token_tracker, console):
        """Test tokens command with no subcommand (defaults to session)."""
        with patch("litai.commands.tokens.console", console):
            handle_tokens_command("", config, token_tracker)


class TestTokenUtilities:
    """Test token utility functions."""

    def test_format_number(self):
        """Test number formatting with thousand separators."""
        test_cases = [
            (0, "0"),
            (123, "123"),
            (1234, "1,234"),
            (1234567, "1,234,567"),
        ]

        for number, expected in test_cases:
            assert format_number(number) == expected

    def test_format_session_summary_compact_empty(self):
        """Test compact session summary formatting with no usage."""
        summary = {"total": 0, "small_model": 0, "large_model": 0}
        result = format_session_summary_compact(summary)
        assert result == "Session: 0 tokens"

    def test_format_session_summary_compact_with_usage(self):
        """Test compact session summary formatting with usage."""
        summary = {"total": 1500, "small_model": 1000, "large_model": 500}
        result = format_session_summary_compact(summary)
        expected = "Session: 1,500 tokens (1,000 small, 500 large)"
        assert result == expected

    def test_format_session_summary_compact_large_numbers(self):
        """Test compact session summary formatting with large numbers."""
        summary = {"total": 1234567, "small_model": 1000000, "large_model": 234567}
        result = format_session_summary_compact(summary)
        expected = "Session: 1,234,567 tokens (1,000,000 small, 234,567 large)"
        assert result == expected


class TestTokenCommandIntegration:
    """Test integration between token commands and token tracker."""

    def test_session_summary_tracking(self, config, token_tracker):
        """Test that session summary correctly tracks usage."""
        # Initially empty
        summary = token_tracker.get_session_summary()
        assert summary["total"] == 0

        # Add some usage
        token_tracker.track_usage(
            TokenUsage(
                input_tokens=100,
                output_tokens=50,
                model="gpt-5-nano",
                model_size="small",
            ),
        )

        # Check updated summary
        summary = token_tracker.get_session_summary()
        assert summary["total"] == 150
        assert summary["small_model"] == 150
        assert summary["large_model"] == 0
        assert summary["requests"] == 1

    def test_mixed_model_usage(self, config, token_tracker):
        """Test tracking with both small and large model usage."""
        # Add small model usage
        token_tracker.track_usage(
            TokenUsage(
                input_tokens=100,
                output_tokens=50,
                model="gpt-5-nano",
                model_size="small",
            ),
        )

        # Add large model usage
        token_tracker.track_usage(
            TokenUsage(
                input_tokens=300,
                output_tokens=200,
                model="gpt-5",
                model_size="large",
            ),
        )

        summary = token_tracker.get_session_summary()
        assert summary["total"] == 650
        assert summary["small_model"] == 150
        assert summary["large_model"] == 500
        assert summary["requests"] == 2
