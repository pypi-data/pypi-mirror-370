"""Tests for logging configuration utilities."""

import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import structlog

from litai.utils.logger import LogConfig, get_logger


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as f:
        log_path = Path(f.name)
    yield log_path
    if log_path.exists():
        log_path.unlink()


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestLogConfig:
    """Test LogConfig class functionality."""

    def test_logconfig_init_defaults(self):
        """Test LogConfig initialization with default parameters."""
        config = LogConfig()

        assert config.debug is False
        assert config.log_level == logging.INFO
        assert config.log_file == Path.home() / ".litai" / "logs" / "litai.log"

    def test_logconfig_init_debug_mode(self):
        """Test LogConfig initialization with debug enabled."""
        config = LogConfig(debug=True)

        assert config.debug is True
        assert config.log_level == logging.DEBUG

    def test_logconfig_init_custom_log_file(self, temp_log_file):
        """Test LogConfig initialization with custom log file."""
        config = LogConfig(log_file=temp_log_file)

        assert config.log_file == temp_log_file

    def test_get_shared_processors(self):
        """Test shared processors are correctly configured."""
        config = LogConfig()
        processors = config.get_shared_processors()

        # Check we have the expected processor types
        processor_types = [type(p).__name__ for p in processors]
        processor_names = [str(p) for p in processors]

        expected_types = [
            "TimeStamper",
            "StackInfoRenderer",
            "CallsiteParameterAdder",
            "ExceptionRenderer",  # format_exc_info returns ExceptionRenderer
        ]

        expected_functions = [
            "merge_contextvars",
            "add_log_level",
        ]

        # Check for processor types
        for expected in expected_types:
            assert any(expected in ptype for ptype in processor_types), (
                f"Missing processor type {expected}"
            )

        # Check for processor functions
        for expected in expected_functions:
            assert any(expected in name for name in processor_names), (
                f"Missing processor function {expected}"
            )

    def test_get_dev_processors(self):
        """Test development processors include shared plus console renderer."""
        config = LogConfig()
        shared_processors = config.get_shared_processors()
        dev_processors = config.get_dev_processors()

        # Dev processors should contain all shared processors plus console renderer
        assert len(dev_processors) == len(shared_processors) + 1

        # Last processor should be console renderer
        last_processor = dev_processors[-1]
        assert hasattr(last_processor, "__name__") or "Console" in str(
            type(last_processor),
        )

    def test_get_prod_processors(self):
        """Test production processors include shared plus JSON renderer."""
        config = LogConfig()
        shared_processors = config.get_shared_processors()
        prod_processors = config.get_prod_processors()

        # Prod processors should contain all shared processors plus two additional
        assert len(prod_processors) == len(shared_processors) + 2

        # Should include dict_tracebacks and JSON renderer
        processor_types = [type(p).__name__ for p in prod_processors]
        assert any(
            "dict_tracebacks" in str(p) or "JSONRenderer" in ptype
            for p, ptype in zip(prod_processors, processor_types, strict=False)
        )

    def test_setup_creates_log_directory(self, temp_log_dir):
        """Test that setup creates the log directory if it doesn't exist."""
        log_file = temp_log_dir / "subdir" / "test.log"
        config = LogConfig(log_file=log_file)

        # Directory shouldn't exist initially
        assert not log_file.parent.exists()

        config.setup()

        # Directory should be created
        assert log_file.parent.exists()
        assert log_file.parent.is_dir()

    def test_setup_configures_logging(self, temp_log_file):
        """Test that setup configures both standard and structured logging."""
        config = LogConfig(debug=True, log_file=temp_log_file)
        config.setup()

        # Check that structlog is configured
        assert structlog.is_configured()

        # Check that we can get a logger
        logger = structlog.get_logger("test")
        assert logger is not None

    @patch("sys.stderr.isatty")
    def test_setup_uses_dev_processors_in_debug_tty(self, mock_isatty, temp_log_file):
        """Test that setup uses dev processors when debug=True and in TTY."""
        mock_isatty.return_value = True
        config = LogConfig(debug=True, log_file=temp_log_file)

        with (
            patch.object(config, "get_dev_processors") as mock_dev,
            patch.object(config, "get_prod_processors") as mock_prod,
        ):
            mock_dev.return_value = []
            mock_prod.return_value = []

            config.setup()

            mock_dev.assert_called_once()
            mock_prod.assert_not_called()

    @patch("sys.stderr.isatty")
    def test_setup_uses_prod_processors_in_non_tty(self, mock_isatty, temp_log_file):
        """Test that setup uses prod processors when not in TTY."""
        mock_isatty.return_value = False
        config = LogConfig(debug=True, log_file=temp_log_file)

        with (
            patch.object(config, "get_dev_processors") as mock_dev,
            patch.object(config, "get_prod_processors") as mock_prod,
        ):
            mock_dev.return_value = []
            mock_prod.return_value = []

            config.setup()

            mock_dev.assert_not_called()
            mock_prod.assert_called_once()

    def test_setup_uses_prod_processors_when_not_debug(self, temp_log_file):
        """Test that setup uses prod processors when debug=False."""
        config = LogConfig(debug=False, log_file=temp_log_file)

        with (
            patch.object(config, "get_dev_processors") as mock_dev,
            patch.object(config, "get_prod_processors") as mock_prod,
        ):
            mock_dev.return_value = []
            mock_prod.return_value = []

            config.setup()

            mock_dev.assert_not_called()
            mock_prod.assert_called_once()



        # Should be able to log with structured data
        logger.info("test message", key="value")

    def test_get_logger_different_names_return_different_loggers(self):
        """Test that different logger names return different instances."""
        LogConfig(debug=True).setup()

        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")

        # They should be different instances but same type
        assert type(logger1) is type(logger2)
        # Different names should give different logger instances
        assert logger1 != logger2


class TestLoggingIntegration:
    """Test integration between components."""

    def test_end_to_end_logging_setup_and_usage(self, temp_log_file, caplog):
        """Test complete logging setup and usage workflow."""
        # Setup logging
        config = LogConfig(debug=True, log_file=temp_log_file)
        config.setup()

        # Get a logger and log something
        logger = get_logger("integration_test")

        with caplog.at_level("INFO"):
            logger.info("test message", operation="test", duration_ms=100)

        # Verify log directory was created
        assert temp_log_file.parent.exists()

        # Check that structlog is properly configured
        assert structlog.is_configured()

        # Should have captured log in caplog (this verifies logging is working)
        assert len(caplog.records) >= 1

        # Verify logger is functional
        logger2 = get_logger("another_logger")
        assert logger2 is not None
        assert hasattr(logger2, "info")

    def test_multiple_loggers_share_configuration(self, temp_log_file):
        """Test that multiple loggers share the same configuration."""
        config = LogConfig(debug=True, log_file=temp_log_file)
        config.setup()

        # Get multiple loggers
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        # Both should be proper structlog loggers
        assert hasattr(logger1, "info")
        assert hasattr(logger2, "info")
        assert type(logger1) is type(logger2)

        # Both should work without errors
        logger1.info("message from logger1")
        logger2.info("message from logger2")

        # Verify log directory exists
        assert temp_log_file.parent.exists()
