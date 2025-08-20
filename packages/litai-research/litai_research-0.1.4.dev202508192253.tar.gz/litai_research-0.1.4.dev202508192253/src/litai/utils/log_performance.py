"""Performance monitoring utilities for operation timing."""

import time
from collections.abc import Generator
from contextlib import contextmanager

import structlog


@contextmanager
def timed_operation(
    operation: str, threshold_ms: float | None = None,
) -> Generator[None, None, None]:
    """Log operation timing, warn if exceeds threshold."""
    logger = structlog.get_logger()
    start = time.perf_counter()

    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        log_data = {"operation": operation, "duration_ms": duration_ms}

        if threshold_ms and duration_ms > threshold_ms:
            logger.warning("slow_operation", **log_data, threshold_ms=threshold_ms)
        else:
            logger.debug("operation_timing", **log_data)
