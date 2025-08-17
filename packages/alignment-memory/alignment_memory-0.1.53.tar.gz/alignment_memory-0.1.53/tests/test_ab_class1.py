from __future__ import annotations

from alignment_memory.a import Class1


def _ev(ts, speaker, text):
    return {"ts": ts, "speaker": speaker, "text": text}


def _sample():
    return [
        _ev("2025-08-15T07:31:00", "user", "?덈뀞"),
        _ev("2025-08-15T07:31:02", "assistant", "諛섍??뚯슂"),
        _ev("2025-08-16T09:00:00", "user", "Hello World"),
        _ev("2025-08-16T10:00:00+09:00", "assistant", "HELLO again"),
        _ev("2025-08-16T00:30:00Z", "system", "hello from Z"),
    ]


def test_text_ignore_case():
    evs = _sample()
    got = Class1.filter_events(evs, text="hello", ignore_case=True)
    assert len(got) == 3


def test_text_case_sensitive():
    evs = _sample()
    got = Class1.filter_events(evs, text="Hello", ignore_case=False)
    assert len(got) == 1


def test_date_range_inclusive():
    evs = _sample()
    got = Class1.filter_events(evs, since="2025-08-16", until="2025-08-16")
    assert len(got) == 3


def test_speaker_filter():
    evs = _sample()
    got = Class1.filter_events(evs, speaker="user")
    assert all(e["speaker"] == "user" for e in got)
    assert len(got) == 2
