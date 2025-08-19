"""Context management utilities for structured logging."""

import contextvars
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import structlog

# Context variables for request tracking
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar[str | None](
    "request_id",
    default=None,
)
operation_var: contextvars.ContextVar[str | None] = contextvars.ContextVar[str | None](
    "operation",
    default=None,
)


@contextmanager
def log_context(**kwargs: Any) -> Generator[None, None, None]:
    """Context manager for adding temporary context to logs.

    Args:
        **kwargs: Key-value pairs to add to the logging context

    Example:
        with log_context(user_id="123", session_id="abc"):
            logger.info("user_action", action="login")
            # Logs will include user_id and session_id automatically
    """
    structlog.contextvars.bind_contextvars(**kwargs)
    try:
        yield
    finally:
        structlog.contextvars.unbind_contextvars(*kwargs.keys())


@contextmanager
def operation_context(operation: str, **kwargs: Any) -> Generator[None, None, None]:
    """Context manager for tracking operations with automatic logging.

    Automatically logs operation start, completion, and failure events.
    Generates a unique operation ID for tracking.

    Args:
        operation: Name of the operation being performed
        **kwargs: Additional context to include in logs

    Example:
        with operation_context("fetch_paper", paper_id="123"):
            # Automatically logs "fetch_paper_started"
            result = fetch_paper_from_api()
            # Automatically logs "fetch_paper_completed" on success
            # Or "fetch_paper_failed" with exception details on error
    """
    operation_id = str(uuid.uuid4())[:8]

    with log_context(
        operation=operation,
        operation_id=operation_id,
        **kwargs,
    ):
        logger = structlog.get_logger()
        logger.info(f"{operation}_started")
        try:
            yield
            logger.info(f"{operation}_completed")
        except Exception as e:
            logger.exception(f"{operation}_failed", error=str(e))
            raise


def clear_context() -> None:
    """Clear all context variables.

    Removes all bound context variables from the current context.
    Useful for cleanup or when starting fresh operations.
    """
    structlog.contextvars.clear_contextvars()


def get_current_context() -> dict[str, Any]:
    """Get the current logging context.

    Returns:
        Dictionary of all currently bound context variables
    """
    return structlog.contextvars.get_contextvars()


def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context.

    Args:
        request_id: Unique identifier for the current request/operation
    """
    request_id_var.set(request_id)
    structlog.contextvars.bind_contextvars(request_id=request_id)


def get_request_id() -> str | None:
    """Get the current request ID.

    Returns:
        The current request ID, or None if not set
    """
    return request_id_var.get()


def set_operation(operation: str) -> None:
    """Set the operation name for the current context.

    Args:
        operation: Name of the current operation
    """
    operation_var.set(operation)
    structlog.contextvars.bind_contextvars(operation=operation)


def get_operation() -> str | None:
    """Get the current operation name.

    Returns:
        The current operation name, or None if not set
    """
    return operation_var.get()
