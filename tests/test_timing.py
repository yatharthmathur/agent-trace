"""Tests for agenttrace.timing — wall-clock span timing helpers."""

import re
import time

from agenttrace.timing import SpanTimer, duration_ms

_RFC3339_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$")


# ── SpanTimer ─────────────────────────────────────────────────────────────────


def test_started_at_is_rfc3339_utc() -> None:
    t = SpanTimer.start()
    assert _RFC3339_UTC.match(t.started_at), f"bad format: {t.started_at!r}"


def test_ended_at_is_rfc3339_utc_after_stop() -> None:
    t = SpanTimer.start()
    t.stop()
    assert t.ended_at is not None
    assert _RFC3339_UTC.match(t.ended_at), f"bad format: {t.ended_at!r}"


def test_ended_at_is_none_before_stop() -> None:
    t = SpanTimer.start()
    assert t.ended_at is None


def test_duration_ms_is_none_before_stop() -> None:
    t = SpanTimer.start()
    assert t.duration_ms is None


def test_duration_ms_is_non_negative_after_stop() -> None:
    t = SpanTimer.start()
    time.sleep(0.01)
    t.stop()
    assert t.duration_ms is not None
    assert t.duration_ms >= 0


def test_duration_ms_reflects_elapsed_time() -> None:
    t = SpanTimer.start()
    time.sleep(0.05)
    t.stop()
    assert t.duration_ms is not None
    # Allow generous bounds: 40 ms - 500 ms for a 50 ms sleep.
    assert 40 <= t.duration_ms <= 500


def test_stop_is_idempotent() -> None:
    t = SpanTimer.start()
    t.stop()
    first_ended_at = t.ended_at
    first_duration = t.duration_ms
    t.stop()
    assert t.ended_at == first_ended_at
    assert t.duration_ms == first_duration


def test_ended_at_is_at_or_after_started_at() -> None:
    t = SpanTimer.start()
    t.stop()
    assert t.ended_at is not None
    assert t.ended_at >= t.started_at


def test_asdict_before_stop() -> None:
    t = SpanTimer.start()
    d = t.asdict()
    assert d["started_at"] == t.started_at
    assert d["ended_at"] is None
    assert d["duration_ms"] is None


def test_asdict_after_stop() -> None:
    t = SpanTimer.start()
    t.stop()
    d = t.asdict()
    assert d["started_at"] == t.started_at
    assert d["ended_at"] == t.ended_at
    assert d["duration_ms"] == t.duration_ms


# ── duration_ms standalone helper ─────────────────────────────────────────────


def test_duration_ms_helper_positive() -> None:
    start = time.perf_counter()
    time.sleep(0.02)
    elapsed = duration_ms(start)
    assert 10 <= elapsed <= 500


def test_duration_ms_helper_zero_when_same_instant() -> None:
    t = time.perf_counter()
    assert duration_ms(t) >= 0


def test_duration_ms_helper_is_float() -> None:
    t = time.perf_counter()
    result = duration_ms(t)
    assert isinstance(result, float)
