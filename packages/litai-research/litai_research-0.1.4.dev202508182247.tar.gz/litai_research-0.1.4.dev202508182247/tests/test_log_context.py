"""Tests for log context management utilities."""

import pytest

from litai.utils.log_context import (
    clear_context,
    get_current_context,
    get_operation,
    get_request_id,
    log_context,
    operation_context,
    set_operation,
    set_request_id,
)
from litai.utils.logger import setup_logging


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Setup logging for tests."""
    setup_logging(debug=True)


def test_log_context_adds_and_removes_context():
    """Test that log_context properly adds and removes context variables."""
    # Start with clean context
    clear_context()

    # Add context and verify it's present
    with log_context(user_id="123", session_id="abc"):
        context = get_current_context()
        assert context["user_id"] == "123"
        assert context["session_id"] == "abc"

    # Context should be cleared after exiting
    context = get_current_context()
    assert "user_id" not in context
    assert "session_id" not in context


def test_operation_context_generates_unique_ids():
    """Test that operation_context generates unique operation IDs."""
    clear_context()

    operation_ids = []

    # Generate multiple operation contexts and collect IDs
    for i in range(3):
        with operation_context("test_op", iteration=i):
            context = get_current_context()
            operation_ids.append(context["operation_id"])

    # All operation IDs should be unique
    assert len(set(operation_ids)) == 3

    # All should be 8 characters long (truncated UUID)
    for op_id in operation_ids:
        assert len(op_id) == 8


def test_operation_context_logs_events(caplog):
    """Test that operation_context logs start/complete events."""
    clear_context()

    with caplog.at_level("INFO"):
        with operation_context("test_operation"):
            pass

    # Should have captured at least start and complete events
    assert len(caplog.records) >= 2, (
        "Should have captured at least start and complete events"
    )

    # Extract log messages and check for events
    log_messages = [str(record.message) for record in caplog.records]
    log_content = " ".join(log_messages)

    assert "test_operation_started" in log_content
    assert "test_operation_completed" in log_content


def test_operation_context_logs_failure_on_exception(caplog):
    """Test that operation_context logs failure events on exception."""
    clear_context()

    with caplog.at_level("INFO"):
        with pytest.raises(ValueError):
            with operation_context("failing_operation"):
                raise ValueError("Test error")

    # Should have logged start and failure events
    assert len(caplog.records) >= 2, (
        "Should have captured at least start and failure events"
    )

    # Extract log messages and check for events
    log_messages = [str(record.message) for record in caplog.records]
    log_content = " ".join(log_messages)

    assert "failing_operation_started" in log_content
    assert "failing_operation_failed" in log_content


def test_clear_context_removes_all_variables():
    """Test that clear_context removes all context variables."""
    # Add some context
    with log_context(key1="value1", key2="value2"):
        assert len(get_current_context()) >= 2

        # Clear context
        clear_context()

        # Context should be empty
        assert get_current_context() == {}


def test_request_id_context_variables():
    """Test request ID context variable functions."""
    clear_context()

    # Initially should be None
    assert get_request_id() is None

    # Set request ID
    set_request_id("req_123")
    assert get_request_id() == "req_123"

    # Should also be in context
    context = get_current_context()
    assert context["request_id"] == "req_123"


def test_operation_context_variables():
    """Test operation context variable functions."""
    clear_context()

    # Initially should be None
    assert get_operation() is None

    # Set operation
    set_operation("test_op")
    assert get_operation() == "test_op"

    # Should also be in context
    context = get_current_context()
    assert context["operation"] == "test_op"


def test_nested_contexts():
    """Test that nested contexts work correctly."""
    clear_context()

    with log_context(outer="value1"):
        outer_context = get_current_context()
        assert outer_context["outer"] == "value1"

        with log_context(inner="value2"):
            inner_context = get_current_context()
            assert inner_context["outer"] == "value1"
            assert inner_context["inner"] == "value2"

        # Inner context should be removed
        after_inner = get_current_context()
        assert after_inner["outer"] == "value1"
        assert "inner" not in after_inner

    # All context should be cleared
    final_context = get_current_context()
    assert "outer" not in final_context
    assert "inner" not in final_context


def test_operation_context_with_additional_kwargs():
    """Test operation_context with additional keyword arguments."""
    clear_context()

    with operation_context("test_op", paper_id="123", user_id="456"):
        context = get_current_context()
        assert context["operation"] == "test_op"
        assert context["paper_id"] == "123"
        assert context["user_id"] == "456"
        assert "operation_id" in context
        assert len(context["operation_id"]) == 8
