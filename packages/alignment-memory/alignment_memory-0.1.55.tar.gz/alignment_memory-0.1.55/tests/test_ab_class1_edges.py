from __future__ import annotations

from alignment_memory.a import Class1


def _ev(ts, speaker, text):
    return {"ts": ts, "speaker": speaker, "text": text}


def _sample():
    # 5 valid events + 1 invalid timestamp
    return [
        _ev("2025-08-16T00:00:00", "u", "hello at start"),  # boundary start (naive -> local)
        _ev("2025-08-16T23:59:59.999999", "u", "hello at end"),  # boundary end (naive -> local)
        _ev("2025-08-16T12:00:00Z", "u", "mid hello Z"),  # UTC Z -> same local day at +09:00
        _ev("2025-08-16T09:00:00+09:00", "a", "HELLO TZ"),  # uppercase variant
        _ev("2025-08-15T10:00:00", "a", "prev day"),  # previous day (naive -> local)
        {"ts": "not-a-date", "speaker": "sys", "text": "bad ts"},  # invalid timestamp
    ]


def test_inclusive_day_range():
    evs = _sample()
    # Expect 4 events from the local calendar day (+09:00)
    got = Class1.filter_events(evs, since="2025-08-16", until="2025-08-16", tz="+09:00")
    assert len(got) == 4


def test_invalid_timestamp_is_skipped():
    evs = _sample()
    # Only valid-timestamp events should remain when no text filter is applied
    got = Class1.filter_events(evs, text=None, tz="+09:00")
    assert len(got) == 5
    assert all(e.get("ts") != "not-a-date" for e in got)


def test_ignore_case_false_is_strict():
    evs = _sample()
    got = Class1.filter_events(evs, text="hello", ignore_case=False, tz="+09:00")
    # Must match only lowercase "hello" (not "HELLO")
    assert all("hello" in e.get("text", "") for e in got)
    assert any("HELLO" in e.get("text", "") for e in evs)  # uppercase exists in the sample
    assert all("HELLO" not in e.get("text", "") for e in got)


def test_text_none_returns_all_valid():
    evs = _sample()
    got = Class1.filter_events(evs, text=None, tz="+09:00")
    assert len(got) == 5
