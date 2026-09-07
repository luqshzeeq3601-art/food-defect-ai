"""Benchmarking and performance metric collection utilities."""

import time
from collections.abc import Callable
from typing import Any


def measure_execution_time(
    fn: Callable[..., Any], *args: Any, **kwargs: Any
) -> tuple[Any, float]:
    """Measure function execution time in milliseconds.

    Args:
        fn: Target callable.
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        Tuple of (Function result, elapsed time in ms).
    """
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    t1 = time.perf_counter()
    elapsed_ms = (t1 - t0) * 1000.0
    return result, elapsed_ms
