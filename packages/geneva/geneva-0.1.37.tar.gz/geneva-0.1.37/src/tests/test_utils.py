# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

import logging
import random
import time

import pytest

from geneva.utils import retry_on_exception


def test_preserves_function_metadata() -> None:
    """Wrapper should preserve __name__ and __doc__ via functools.wraps."""

    def fn(a, b) -> int:
        """original doc"""
        return a + b

    wrapped = retry_on_exception()(fn)
    assert wrapped.__name__ == fn.__name__
    assert wrapped.__doc__ == fn.__doc__


def test_success_no_retries(monkeypatch) -> None:
    """If the function succeeds immediately, no sleep or warning should occur."""
    called = []

    def fast_fn(x) -> list:
        called.append(x)
        return x * 2

    # spy on sleep and uniform
    monkeypatch.setattr(
        time,
        "sleep",
        lambda s: (_ for _ in ()).throw(AssertionError("sleep should not be called")),
    )
    monkeypatch.setattr(random, "uniform", lambda a, b: b)

    wrapped = retry_on_exception(max_attempts=3, initial_delay=1.0, backoff_factor=2.0)(
        fast_fn
    )
    result = wrapped(10)
    assert result == 20
    assert called == [10]


def test_retries_and_backoff(monkeypatch, caplog) -> None:
    """Function fails twice then succeeds on 3rd attempt with correct sleep calls and
    logs."""
    attempts = {"count": 0}
    sleep_calls = []

    def flaky(x) -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise ValueError(f"fail #{attempts['count']}")
        return "ok"

    # force deterministic jitter = full delay
    monkeypatch.setattr(random, "uniform", lambda a, b: b)
    # record sleep calls
    monkeypatch.setattr(time, "sleep", lambda s: sleep_calls.append(s))

    # capture warnings
    caplog.set_level(logging.WARNING)

    wrapped = retry_on_exception(
        max_attempts=5, initial_delay=1.0, backoff_factor=2.0, exceptions=(ValueError,)
    )(flaky)

    res = wrapped(0)
    assert res == "ok"

    # first failure: delay = 1.0 → sleep(1.0)
    # second failure: delay = 1.0*2 = 2.0 → sleep(2.0)
    assert sleep_calls == [1.0, 2.0]

    # check that two warning logs were emitted
    warning_texts = [
        r.getMessage() for r in caplog.records if r.levelno == logging.WARNING
    ]
    assert any("Attempt 1 for flaky failed with" in text for text in warning_texts)
    assert any("Attempt 2 for flaky failed with" in text for text in warning_texts)


def test_max_attempts_exhaustion(monkeypatch, caplog) -> None:
    """After max_attempts is reached, the exception is re-raised and an error is
    logged."""

    def always_fail() -> None:
        raise ValueError("no hope")

    sleep_calls = []
    monkeypatch.setattr(random, "uniform", lambda a, b: 0)  # jitter=0 for clarity
    monkeypatch.setattr(time, "sleep", lambda s: sleep_calls.append(s))

    caplog.set_level(logging.ERROR)
    wrapped = retry_on_exception(max_attempts=2, initial_delay=0.5, backoff_factor=2.0)(
        always_fail
    )

    with pytest.raises(ValueError, match="no hope"):
        wrapped()

    # should have slept once (only one retry before giving up)
    assert sleep_calls == [0]

    # check error log
    errors = [r.getMessage() for r in caplog.records if r.levelno == logging.ERROR]
    assert any(
        "always_fail' failed after 2 attempts; giving up." in msg for msg in errors
    )


def test_non_retryable_exception(monkeypatch) -> None:
    """Exceptions not in the tuple should propagate immediately (no retry)."""
    sleep_calls = []
    monkeypatch.setattr(time, "sleep", lambda s: sleep_calls.append(s))

    @retry_on_exception(max_attempts=5, exceptions=(ValueError,))
    def raises_type() -> None:
        raise TypeError("wrong kind")

    with pytest.raises(TypeError):
        raises_type()

    assert sleep_calls == []  # no backoff/sleep occurred
