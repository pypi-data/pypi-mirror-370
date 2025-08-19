# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# dumping ground for utility functions

import datetime
import functools
import logging
import random
import time
from typing import Any

_LOG = logging.getLogger(__name__)


def retry_on_exception(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Any:
    """
    Decorator to retry a function on exception with exponential backoff.

    :param max_attempts: Total number of attempts (including the first).
    :param initial_delay: Seconds to wait before first retry.
    :param backoff_factor: Multiplier for delay after each failed attempt.
    :param exceptions: Tuple of exception classes to catch and retry on.
    :param warning_message: Template for warning log (see docstring).
    """

    def decorator(func) -> Any:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:  # noqa: PERF203
                    if attempt >= max_attempts:
                        _LOG.error(
                            f"{func.__name__!r} failed after {attempt} attempts;"
                            " giving up.",
                            exc_info=True,
                        )
                        raise
                    # log the custom warning
                    sleep_time = random.uniform(0, delay)  # jitter
                    _LOG.warning(
                        f"Attempt {attempt} for {func.__name__} failed with {exc!r}; "
                        f"retrying in {sleep_time:.1f}s..."
                    )
                    time.sleep(sleep_time)
                    delay *= backoff_factor
                    attempt += 1

        return wrapper

    return decorator


def dt_now_utc() -> datetime.datetime:
    """Return the current UTC datetime."""
    return datetime.datetime.now(datetime.timezone.utc)
