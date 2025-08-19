"""Tests for token tracking functionality."""

import json
import shutil
import tempfile
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

import pytest

from litai.config import Config
from litai.llm import LLMClient
from litai.token_tracker import TokenStats, TokenTracker, TokenUsage


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def config(temp_dir: Path) -> Config:
    """Create a config instance with temporary directory."""
    return Config(temp_dir)


@pytest.fixture
def token_tracker(config: Config) -> TokenTracker:
    """Create a TokenTracker instance."""
    return TokenTracker(config)


class TestTokenUsage:
    """Test TokenUsage dataclass."""

    def test_token_usage_creation(self) -> None:
        """Test basic TokenUsage creation."""
        usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            model="gpt-5-nano",
            model_size="small",
            operation_type="search",
        )

        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.model == "gpt-5-nano"
        assert usage.model_size == "small"
        assert usage.operation_type == "search"
        assert isinstance(usage.timestamp, datetime)

    def test_token_usage_defaults(self) -> None:
        """Test TokenUsage with default values."""
        usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            model="gpt-5",
            model_size="large",
        )

        assert usage.operation_type == ""
        assert isinstance(usage.timestamp, datetime)


class TestTokenStats:
    """Test TokenStats dataclass."""

    def test_token_stats_creation(self) -> None:
        """Test basic TokenStats creation."""
        stats = TokenStats(
            small_model_input=100,
            small_model_output=50,
            large_model_input=200,
            large_model_output=100,
            total_requests=5,
        )

        assert stats.small_model_input == 100
        assert stats.small_model_output == 50
        assert stats.large_model_input == 200
        assert stats.large_model_output == 100
        assert stats.total_requests == 5

    def test_token_stats_defaults(self) -> None:
        """Test TokenStats with default values."""
        stats = TokenStats()

        assert stats.small_model_input == 0
        assert stats.small_model_output == 0
        assert stats.large_model_input == 0
        assert stats.large_model_output == 0
        assert stats.total_requests == 0

    def test_small_model_total(self) -> None:
        """Test small_model_total property."""
        stats = TokenStats(
            small_model_input=100,
            small_model_output=50,
        )

        assert stats.small_model_total == 150

    def test_large_model_total(self) -> None:
        """Test large_model_total property."""
        stats = TokenStats(
            large_model_input=200,
            large_model_output=100,
        )

        assert stats.large_model_total == 300

    def test_total_tokens(self) -> None:
        """Test total_tokens property."""
        stats = TokenStats(
            small_model_input=100,
            small_model_output=50,
            large_model_input=200,
            large_model_output=100,
        )

        assert stats.total_tokens == 450


class TestTokenTracker:
    """Test TokenTracker class."""

    def test_token_tracker_initialization(
        self, token_tracker: TokenTracker, config: Config,
    ) -> None:
        """Test TokenTracker initialization."""
        assert token_tracker.config == config
        assert token_tracker.usage_file == config.data_dir / "token_usage.json"
        assert token_tracker.session_usage == []
        assert isinstance(token_tracker.stats, TokenStats)

    def test_token_usage_tracking(self, token_tracker: TokenTracker) -> None:
        """Test basic token usage recording."""
        usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            model="gpt-5-nano",
            model_size="small",
            operation_type="search",
        )

        token_tracker.track_usage(usage)

        # Check session usage
        assert len(token_tracker.session_usage) == 1
        assert token_tracker.session_usage[0] == usage

        # Check stats
        assert token_tracker.stats.small_model_input == 100
        assert token_tracker.stats.small_model_output == 50
        assert token_tracker.stats.large_model_input == 0
        assert token_tracker.stats.large_model_output == 0
        assert token_tracker.stats.total_requests == 1

    def test_large_model_tracking(self, token_tracker: TokenTracker) -> None:
        """Test large model token tracking."""
        usage = TokenUsage(
            input_tokens=200,
            output_tokens=100,
            model="gpt-5",
            model_size="large",
            operation_type="synthesis",
        )

        token_tracker.track_usage(usage)

        # Check stats
        assert token_tracker.stats.small_model_input == 0
        assert token_tracker.stats.small_model_output == 0
        assert token_tracker.stats.large_model_input == 200
        assert token_tracker.stats.large_model_output == 100
        assert token_tracker.stats.total_requests == 1

    def test_model_size_separation(self, token_tracker: TokenTracker) -> None:
        """Test separate tracking for small vs large models."""
        small_usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            model="gpt-5-nano",
            model_size="small",
            operation_type="search",
        )

        large_usage = TokenUsage(
            input_tokens=200,
            output_tokens=100,
            model="gpt-5",
            model_size="large",
            operation_type="synthesis",
        )

        token_tracker.track_usage(small_usage)
        token_tracker.track_usage(large_usage)

        # Check separation
        assert token_tracker.stats.small_model_input == 100
        assert token_tracker.stats.small_model_output == 50
        assert token_tracker.stats.large_model_input == 200
        assert token_tracker.stats.large_model_output == 100
        assert token_tracker.stats.total_requests == 2
        assert len(token_tracker.session_usage) == 2

    def test_session_summary(self, token_tracker: TokenTracker) -> None:
        """Test session summary calculations."""
        # Test empty session
        summary = token_tracker.get_session_summary()
        assert summary == {
            "total": 0,
            "small_model": 0,
            "large_model": 0,
            "requests": 0,
        }

        # Add some usage
        small_usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            model="gpt-5-nano",
            model_size="small",
        )

        large_usage = TokenUsage(
            input_tokens=200,
            output_tokens=100,
            model="gpt-5",
            model_size="large",
        )

        token_tracker.track_usage(small_usage)
        token_tracker.track_usage(large_usage)

        summary = token_tracker.get_session_summary()
        assert summary["total"] == 450  # 150 + 300
        assert summary["small_model"] == 150
        assert summary["large_model"] == 300
        assert summary["requests"] == 2

    def test_persistent_storage(
        self, token_tracker: TokenTracker, config: Config,
    ) -> None:
        """Test saving/loading statistics to disk."""
        usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            model="gpt-5-nano",
            model_size="small",
            operation_type="test",
        )

        token_tracker.track_usage(usage)

        # Check file was created and has correct content
        assert token_tracker.usage_file.exists()

        data = json.loads(token_tracker.usage_file.read_text())
        assert data["small_model_input"] == 100
        assert data["small_model_output"] == 50
        assert data["large_model_input"] == 0
        assert data["large_model_output"] == 0
        assert data["total_requests"] == 1

        # Test loading
        new_tracker = TokenTracker(config)
        assert new_tracker.stats.small_model_input == 100
        assert new_tracker.stats.small_model_output == 50
        assert new_tracker.stats.total_requests == 1

    def test_load_stats_file_not_exists(self, config: Config) -> None:
        """Test loading stats when file doesn't exist."""
        tracker = TokenTracker(config)

        # Should create default stats
        assert tracker.stats.small_model_input == 0
        assert tracker.stats.total_requests == 0

    def test_load_stats_invalid_json(self, config: Config) -> None:
        """Test loading stats with invalid JSON file."""
        # Create invalid JSON file
        usage_file = config.data_dir / "token_usage.json"
        usage_file.write_text("invalid json")

        tracker = TokenTracker(config)

        # Should fallback to default stats
        assert tracker.stats.small_model_input == 0
        assert tracker.stats.total_requests == 0

    def test_track_usage_error_handling(
        self, token_tracker: TokenTracker, monkeypatch,
    ) -> None:
        """Test that tracking errors don't break the application."""

        # Mock _save_stats to raise an exception
        def mock_save_stats():
            raise OSError("Permission denied")

        monkeypatch.setattr(token_tracker, "_save_stats", mock_save_stats)

        usage = TokenUsage(
            input_tokens=100,
            output_tokens=50,
            model="gpt-5-nano",
            model_size="small",
        )

        # Should not raise exception
        token_tracker.track_usage(usage)

        # Usage should still be in session
        assert len(token_tracker.session_usage) == 1


class TestLLMClientIntegration:
    """Test integration with LLMClient completion calls."""

    def test_llm_client_without_config(self) -> None:
        """Test LLMClient without config doesn't have token tracker."""
        client = LLMClient()
        assert client.token_tracker is None
