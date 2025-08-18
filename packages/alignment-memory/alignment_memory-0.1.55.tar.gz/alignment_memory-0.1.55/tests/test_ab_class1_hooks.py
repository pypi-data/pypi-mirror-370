from __future__ import annotations

from alignment_memory.a import Class1


def _ev(ts, speaker, text):
    return {"ts": ts, "speaker": speaker, "text": text}


def _sample():
    return [
        _ev("2025-08-16T09:00:00", "user", "hello one"),
        _ev("2025-08-16T09:01:00", "assistant", "hello two"),
        _ev("2025-08-16T09:02:00Z", "system", "hello three"),
    ]


def test_pre_filter_drops_event():
    evs = _sample() + [
        {"ts": "2025-08-16T09:03:00", "speaker": "user"},  # text ?놁쓬 ??pre?먯꽌 ?쒕엻
    ]

    def pre(ev):
        return ev if "text" in ev else None

    got = Class1.filter_events(evs, text="hello", ignore_case=True, pre_filter=pre)
    assert all("text" in g for g in got)


def test_post_filter_masks_text():
    evs = [_ev("2025-08-16T10:00:00", "user", "id=1234 hello")]

    def post(ev):
        ev = dict(ev)
        ev["text"] = ev["text"].replace("1234", "****")
        return ev

    got = Class1.filter_events(evs, text="hello", ignore_case=True, post_filter=post)
    assert got[0]["text"] == "id=**** hello"


def test_score_sort_desc():
    evs = [
        _ev("2025-08-16T00:00:00Z", "s", "a"),
        _ev("2025-08-16T01:00:00Z", "s", "b"),
        _ev("2025-08-16T02:00:00Z", "s", "c"),
    ]

    def score(ev):
        return {"a": 0.1, "b": 0.9, "c": 0.5}[ev["text"]]

    got = Class1.filter_events(evs, sort="desc", sort_by="score", score_fn=score)
    assert [g["text"] for g in got] == ["b", "c", "a"]


def test_score_none_falls_back_and_keeps_ts():
    evs = [
        _ev("2025-08-16T00:00:00Z", "s", "x"),
        _ev("2025-08-16T01:00:00Z", "s", "y"),
    ]

    def score(ev):
        return None  # ?먯닔 ?놁쓬 ??ts濡??뺣젹

    got = Class1.filter_events(evs, sort="asc", sort_by="score", score_fn=score)
    assert [g["text"] for g in got] == ["x", "y"]
