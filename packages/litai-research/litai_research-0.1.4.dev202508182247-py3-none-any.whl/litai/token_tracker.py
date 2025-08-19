"""Token usage tracking for LitAI."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from litai.utils.logger import get_logger

if TYPE_CHECKING:
    from .config import Config

logger = get_logger(__name__)


@dataclass
class TokenUsage:
    """Track token usage for a single request."""

    input_tokens: int
    output_tokens: int
    model: str
    model_size: str  # "small" or "large"
    timestamp: datetime = field(default_factory=datetime.now)
    operation_type: str = ""  # "synthesis", "search", "classification", etc.


@dataclass
class TokenStats:
    """Aggregate token statistics."""

    small_model_input: int = 0
    small_model_output: int = 0
    large_model_input: int = 0
    large_model_output: int = 0
    total_requests: int = 0

    @property
    def small_model_total(self) -> int:
        """Total tokens used by small model."""
        return self.small_model_input + self.small_model_output

    @property
    def large_model_total(self) -> int:
        """Total tokens used by large model."""
        return self.large_model_input + self.large_model_output

    @property
    def total_tokens(self) -> int:
        """Total tokens used across all models."""
        return self.small_model_total + self.large_model_total


class TokenTracker:
    """Track and persist token usage statistics."""

    def __init__(self, config: "Config"):
        """Initialize token tracker with configuration.

        Args:
            config: LitAI configuration instance
        """
        self.config = config
        self.usage_file = config.data_dir / "token_usage.json"
        self.session_usage: list[TokenUsage] = []
        self.stats = self._load_stats()

        logger.info("token_tracker_initialized", usage_file=str(self.usage_file))

    def track_usage(self, usage: TokenUsage) -> None:
        """Record token usage for a request.

        Args:
            usage: TokenUsage instance with request details
        """
        try:
            self.session_usage.append(usage)

            # Update aggregate stats
            if usage.model_size == "small":
                self.stats.small_model_input += usage.input_tokens
                self.stats.small_model_output += usage.output_tokens
            else:
                self.stats.large_model_input += usage.input_tokens
                self.stats.large_model_output += usage.output_tokens

            self.stats.total_requests += 1
            self._save_stats()

            logger.debug(
                "token_usage_tracked",
                model=usage.model,
                model_size=usage.model_size,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                operation_type=usage.operation_type,
            )

        except Exception as e:
            logger.error("failed_to_track_token_usage", error=str(e))
            # Don't raise - token tracking shouldn't break the main flow

    def get_session_summary(self) -> dict[str, int]:
        """Get token usage summary for current session.

        Returns:
            Dictionary with session usage statistics
        """
        if not self.session_usage:
            return {"total": 0, "small_model": 0, "large_model": 0, "requests": 0}

        small_total = sum(
            u.input_tokens + u.output_tokens
            for u in self.session_usage
            if u.model_size == "small"
        )
        large_total = sum(
            u.input_tokens + u.output_tokens
            for u in self.session_usage
            if u.model_size == "large"
        )

        return {
            "total": small_total + large_total,
            "small_model": small_total,
            "large_model": large_total,
            "requests": len(self.session_usage),
        }

    def _load_stats(self) -> TokenStats:
        """Load persistent token statistics from disk.

        Returns:
            TokenStats instance with loaded or default values
        """
        if not self.usage_file.exists():
            logger.debug("token_usage_file_not_found", creating_new=True)
            return TokenStats()

        try:
            data = json.loads(self.usage_file.read_text())
            stats = TokenStats(**data)
            logger.info(
                "token_stats_loaded",
                total_tokens=stats.total_tokens,
                total_requests=stats.total_requests,
            )
            return stats
        except Exception as e:
            logger.error(
                "failed_to_load_token_stats", error=str(e), using_defaults=True,
            )
            return TokenStats()

    def _save_stats(self) -> None:
        """Save token statistics to disk.

        Fails silently if unable to save to avoid disrupting the main application flow.
        """
        try:
            # Ensure parent directory exists
            self.usage_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "small_model_input": self.stats.small_model_input,
                "small_model_output": self.stats.small_model_output,
                "large_model_input": self.stats.large_model_input,
                "large_model_output": self.stats.large_model_output,
                "total_requests": self.stats.total_requests,
            }

            self.usage_file.write_text(json.dumps(data, indent=2))

            logger.debug(
                "token_stats_saved",
                total_tokens=self.stats.total_tokens,
                total_requests=self.stats.total_requests,
            )

        except Exception as e:
            logger.error("failed_to_save_token_stats", error=str(e))
            # Fail silently - token tracking is not critical for application function
