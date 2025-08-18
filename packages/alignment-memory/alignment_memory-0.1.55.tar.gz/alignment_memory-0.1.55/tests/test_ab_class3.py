from __future__ import annotations

from datetime import UTC, datetime

from alignment_memory.a.class3 import Class3, RankConfig


def _ev(ts, speaker, text, **kw):
    ev = {"ts": ts, "speaker": speaker, "text": text}
    ev.update(kw)
    return ev


NOW = datetime(2025, 8, 16, 12, 0, 0, tzinfo=UTC)


def test_recency_orders_when_base_equal():
    evs = [
        _ev("2025-08-16T09:00:00Z", "u", "a"),
        _ev("2025-08-16T10:00:00Z", "u", "b"),
        _ev("2025-08-16T11:00:00Z", "u", "c"),
    ]
    cfg = RankConfig(half_life_hours=1.0, recency_weight=1.0, annotate=False)
    got = Class3.rank(evs, score_fn=None, now=NOW, config=cfg)
    assert [g["text"] for g in got] == ["c", "b", "a"]


def test_score_fn_can_outweigh_recency():
    evs = [
        _ev("2025-08-16T11:59:00Z", "u", "near"),
        _ev("2025-08-15T12:00:00Z", "u", "old-but-high"),
    ]

    def score(ev):
        return 10.0 if ev["text"] == "old-but-high" else 0.0

    cfg = RankConfig(half_life_hours=1.0, recency_weight=0.5, annotate=False)
    got = Class3.rank(evs, score_fn=score, now=NOW, config=cfg)
    assert got[0]["text"] == "old-but-high"


def test_dedup_best_keeps_highest_score():
    evs = [
        _ev("2025-08-16T10:00:00Z", "u", "dup"),
        _ev("2025-08-16T11:00:00Z", "u", "dup"),
    ]

    def score(ev):
        return 0.1 if ev["ts"].endswith("10:00:00Z") else 0.9

    cfg = RankConfig(dedup_by=("text", "speaker"), dedup_strategy="best", annotate=False)
    got = Class3.rank(evs, score_fn=score, now=NOW, config=cfg)
    assert len(got) == 1 and got[0]["ts"].endswith("11:00:00Z")


def test_session_weights_and_current_boost():
    evs = [
        _ev("2025-08-16T10:00:00Z", "u", "x", sid="s1"),
        _ev("2025-08-16T11:00:00Z", "u", "y", sid="s2"),
    ]

    def score(ev):
        return 0.0

    cfg = RankConfig(
        session_weights={"s1": 2.0, "s2": 1.0},
        current_session="s2",
        current_session_boost=0.5,
        recency_weight=0.5,
    )
    got = Class3.rank(evs, score_fn=score, now=NOW, config=cfg)
    assert len(got) == 2 and {g["text"] for g in got} == {"x", "y"}


def test_limit_and_annotation():
    evs = [
        _ev("2025-08-16T08:00:00Z", "u", "a"),
        _ev("2025-08-16T09:00:00Z", "u", "b"),
        _ev("2025-08-16T10:00:00Z", "u", "c"),
    ]
    cfg = RankConfig(annotate=True, recency_weight=1.0, half_life_hours=2.0)
    got = Class3.rank(evs, score_fn=None, now=NOW, config=cfg, limit=2)
    assert len(got) == 2 and all("rank_score" in g and "rank_recency" in g for g in got)
