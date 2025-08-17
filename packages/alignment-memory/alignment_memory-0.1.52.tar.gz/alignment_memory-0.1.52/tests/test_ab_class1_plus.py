from __future__ import annotations

from datetime import UTC, datetime

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


def test_regex_case_insensitive():
    evs = _sample()
    got = Class1.filter_events(evs, text=r"^hello\b", text_mode="regex", ignore_case=True)
    assert len(got) == 3  # Hello World / HELLO again / hello from Z


def test_exact_match():
    evs = _sample()
    got = Class1.filter_events(evs, text="HELLO again", text_mode="exact", ignore_case=False)
    assert len(got) == 1 and got[0]["text"] == "HELLO again"


def test_speakers_list():
    evs = _sample()
    got = Class1.filter_events(evs, speakers=["user", "system"], text="hello", ignore_case=True)
    # assistant???덉슜 紐⑸줉???놁쑝誘濡??쒖쇅 ??user+system ??嫄댁씠 ?뺣떟
    assert len(got) == 2 and all(g["speaker"] in ("user", "system") for g in got)


def test_epoch_and_datetime_ts():
    evs = _sample()
    evs.append(_ev(0, "epocher", "hello epoch"))  # epoch seconds
    evs.append(_ev(datetime(2025, 8, 16, 12, 0, 0, tzinfo=UTC), "dt", "hello dt"))
    got = Class1.filter_events(evs, text="hello", ignore_case=True)
    assert len(got) == 5


def test_sort_limit_offset():
    evs = [
        _ev("2025-01-01T00:00:00Z", "s", "t1"),
        _ev("2025-01-01T01:00:00Z", "s", "t2"),
        _ev("2025-01-01T02:00:00Z", "s", "t3"),
    ]
    got = Class1.filter_events(evs, sort="desc", offset=1, limit=1)
    assert len(got) == 1 and got[0]["text"] == "t2"
