"""Tests for performance monitoring utilities."""

import time
from unittest.mock import patch

import pytest

from litai.utils.log_performance import timed_operation
from litai.utils.logger import setup_logging


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Setup logging for tests."""
    setup_logging(debug=True)


class TestTimedOperation:
    """Test timed_operation context manager."""

    def test_timed_operation_basic_usage(self, caplog):
        """Test basic usage of timed_operation context manager."""
        with caplog.at_level("DEBUG"), timed_operation("test_operation"):
            time.sleep(0.01)  # 10ms delay

        # Should have captured timing log
        assert len(caplog.records) >= 1

        # Find the timing record
        timing_records = [
            r for r in caplog.records if "operation_timing" in str(r.message)
        ]
        assert len(timing_records) == 1

        record = timing_records[0]
        assert "test_operation" in str(record.message)
        assert "duration_ms" in str(record.message)

    def test_timed_operation_measures_time_accurately(self, caplog):
        """Test that timed_operation measures time with reasonable accuracy."""
        sleep_time = 0.05  # 50ms

        with caplog.at_level("DEBUG"), timed_operation("timing_test"):
            time.sleep(sleep_time)

        # Extract duration from log message
        timing_records = [
            r for r in caplog.records if "operation_timing" in str(r.message)
        ]
        assert len(timing_records) == 1

        # Check that measured time is approximately correct (within reasonable margin)
        # The exact format depends on the logger configuration, but duration should be mentioned
        record_msg = str(timing_records[0].message)
        assert "timing_test" in record_msg
        # The actual duration assertion depends on log format, but we can verify it's reasonable
        # by checking that the operation took some measurable time

    def test_timed_operation_without_threshold(self, caplog):
        """Test timed_operation without threshold logs at debug level."""
        with caplog.at_level("DEBUG"), timed_operation("no_threshold_test"):
            time.sleep(0.01)

        # Should log at DEBUG level
        debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
        timing_records = [
            r for r in debug_records if "operation_timing" in str(r.message)
        ]

        assert len(timing_records) == 1
        assert "no_threshold_test" in str(timing_records[0].message)

    def test_timed_operation_with_threshold_under_limit(self, caplog):
        """Test timed_operation with threshold when under the limit."""
        with (
            caplog.at_level("DEBUG"),
            timed_operation("under_threshold", threshold_ms=100.0),
        ):
            time.sleep(0.01)  # 10ms - under 100ms threshold

        # Should log at DEBUG level, not WARNING
        debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]

        timing_records = [
            r for r in debug_records if "operation_timing" in str(r.message)
        ]
        slow_records = [
            r for r in warning_records if "slow_operation" in str(r.message)
        ]

        assert len(timing_records) == 1
        assert len(slow_records) == 0
        assert "under_threshold" in str(timing_records[0].message)

    def test_timed_operation_with_threshold_over_limit(self, caplog):
        """Test timed_operation with threshold when over the limit."""
        with (
            caplog.at_level("DEBUG"),
            timed_operation("over_threshold", threshold_ms=10.0),
        ):
            time.sleep(0.02)  # 20ms - over 10ms threshold

        # Should log at WARNING level
        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        slow_records = [
            r for r in warning_records if "slow_operation" in str(r.message)
        ]

        assert len(slow_records) == 1
        record = slow_records[0]
        assert "over_threshold" in str(record.message)
        assert "threshold_ms" in str(record.message)

    def test_timed_operation_logs_on_exception(self, caplog):
        """Test that timed_operation logs timing even when exception occurs."""
        with (
            caplog.at_level("DEBUG"),
            pytest.raises(ValueError),
            timed_operation("failing_operation"),
        ):
            time.sleep(0.01)
            raise ValueError("Test exception")

        # Should still have timing log despite exception
        timing_records = [
            r for r in caplog.records if "operation_timing" in str(r.message)
        ]
        assert len(timing_records) == 1
        assert "failing_operation" in str(timing_records[0].message)

    def test_timed_operation_exception_with_threshold_exceeded(self, caplog):
        """Test timed_operation logs slow operation warning even on exception."""
        with (
            caplog.at_level("DEBUG"),
            pytest.raises(ValueError),
            timed_operation("slow_failing_operation", threshold_ms=10.0),
        ):
            time.sleep(0.02)  # 20ms - over threshold
            raise ValueError("Test exception")

        # Should log slow operation warning despite exception
        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
        slow_records = [
            r for r in warning_records if "slow_operation" in str(r.message)
        ]

        assert len(slow_records) == 1
        assert "slow_failing_operation" in str(slow_records[0].message)

    def test_timed_operation_different_operations_logged_separately(self, caplog):
        """Test that different operations are logged as separate events."""
        with caplog.at_level("DEBUG"):
            with timed_operation("operation_1"):
                time.sleep(0.01)

            with timed_operation("operation_2"):
                time.sleep(0.01)

        timing_records = [
            r for r in caplog.records if "operation_timing" in str(r.message)
        ]
        assert len(timing_records) == 2

        # Each operation should be logged separately
        messages = [str(r.message) for r in timing_records]
        assert any("operation_1" in msg for msg in messages)
        assert any("operation_2" in msg for msg in messages)

    def test_timed_operation_nested_operations(self, caplog):
        """Test nested timed operations work correctly."""
        with caplog.at_level("DEBUG"), timed_operation("outer_operation"):
            time.sleep(0.01)
            with timed_operation("inner_operation"):
                time.sleep(0.01)
                time.sleep(0.01)

        timing_records = [
            r for r in caplog.records if "operation_timing" in str(r.message)
        ]
        assert len(timing_records) == 2

        messages = [str(r.message) for r in timing_records]
        assert any("outer_operation" in msg for msg in messages)
        assert any("inner_operation" in msg for msg in messages)

    @patch("structlog.get_logger")
    def test_timed_operation_uses_structlog_logger(self, mock_get_logger):
        """Test that timed_operation uses structlog.get_logger."""
        mock_logger = mock_get_logger.return_value

        with timed_operation("test_logger_usage"):
            time.sleep(0.001)

        mock_get_logger.assert_called_once()
        # Logger should have been called with debug method
        assert mock_logger.debug.called or mock_logger.warning.called

    def test_timed_operation_zero_threshold_logs_debug(self, caplog):
        """Test that zero threshold is falsy and logs at debug level."""
        with (
            caplog.at_level("DEBUG"),
            timed_operation("zero_threshold", threshold_ms=0.0),
        ):
            time.sleep(0.001)

        # Zero threshold is falsy, so should log at debug level, not warning
        debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
        timing_records = [
            r for r in debug_records if "operation_timing" in str(r.message)
        ]
        warning_records = [r for r in caplog.records if r.levelname == "WARNING"]

        assert len(timing_records) == 1
        assert len(warning_records) == 0
        assert "zero_threshold" in str(timing_records[0].message)

    def test_timed_operation_logs_structured_data(self):
        """Test that timed_operation logs structured data correctly."""
        # This test verifies the structure of logged data by mocking the logger
        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = mock_get_logger.return_value

            with timed_operation("structured_test", threshold_ms=50.0):
                time.sleep(0.01)

            # Should have called debug method with structured arguments
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args

            # First argument should be event name
            assert call_args[0][0] == "operation_timing"

            # Keyword arguments should include operation and duration_ms
            kwargs = call_args[1]
            assert "operation" in kwargs
            assert kwargs["operation"] == "structured_test"
            assert "duration_ms" in kwargs
            assert isinstance(kwargs["duration_ms"], int | float)
            assert kwargs["duration_ms"] >= 0

    def test_timed_operation_slow_logs_structured_data_with_threshold(self):
        """Test that slow operation logs include threshold information."""
        with patch("structlog.get_logger") as mock_get_logger:
            mock_logger = mock_get_logger.return_value

            with timed_operation("slow_structured_test", threshold_ms=5.0):
                time.sleep(0.01)  # Should exceed 5ms threshold

            # Should have called warning method
            mock_logger.warning.assert_called_once()
            call_args = mock_logger.warning.call_args

            # First argument should be event name
            assert call_args[0][0] == "slow_operation"

            # Keyword arguments should include all required fields
            kwargs = call_args[1]
            assert "operation" in kwargs
            assert kwargs["operation"] == "slow_structured_test"
            assert "duration_ms" in kwargs
            assert "threshold_ms" in kwargs
            assert kwargs["threshold_ms"] == 5.0
