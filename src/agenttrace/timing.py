"""Wall-clock timing helpers for traced spans.

SpanTimer records started_at / ended_at as UTC RFC 3339 strings and
duration_ms as a float. It uses time.perf_counter for elapsed precision
and datetime.now(UTC) for absolute timestamps.

Usage::

    timer = SpanTimer.start()
    try:
        result = fn(*args, **kwargs)
    finally:
        timer.stop()

    record = {
        **timer.asdict(),
        "name": fn.__name__,
        ...
    }
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

_UTC = timezone.utc


def _utc_now_rfc3339() -> str:
    """Return the current UTC time as a RFC 3339 string with microseconds."""
    return datetime.now(_UTC).strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def duration_ms(perf_start: float) -> float:
    """Return milliseconds elapsed since a perf_counter snapshot."""
    return (time.perf_counter() - perf_start) * 1000.0


@dataclass
class SpanTimer:
    """Immutable start timestamp with an optional stop moment.

    Use SpanTimer.start() to create; call .stop() once when the work
    finishes. Calling .stop() a second time is a no-op.
    """

    started_at: str
    ended_at: str | None = field(default=None)
    duration_ms: float | None = field(default=None)

    # Not exposed publicly — used only by stop().
    _perf_start: float = field(default=0.0, repr=False)

    @classmethod
    def start(cls) -> SpanTimer:
        """Capture the current wall clock and return a running timer."""
        return cls(
            started_at=_utc_now_rfc3339(),
            _perf_start=time.perf_counter(),
        )

    def stop(self) -> None:
        """Record ended_at and duration_ms. Idempotent after first call."""
        if self.ended_at is not None:
            return
        self.ended_at = _utc_now_rfc3339()
        self.duration_ms = (time.perf_counter() - self._perf_start) * 1000.0

    def asdict(self) -> dict[str, str | float | None]:
        """Return the timing fields as a plain dict for span records."""
        return {
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_ms": self.duration_ms,
        }
