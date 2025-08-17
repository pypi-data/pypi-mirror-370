from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .b import Class1 as _C1


@dataclass
class RankConfig:
    half_life_hours: float = 6.0
    recency_weight: float = 1.0
    session_weights: dict[str, float] | None = None  # {"sid": weight}
    current_session: str | None = None
    current_session_boost: float = 0.0
    dedup_by: Sequence[str] | None = None
    dedup_strategy: str = "best"  # "best" | "first" | "last"
    annotate: bool = False


class Class3:
    """Ranking 시스템: recency/세션/스코어/중복제거"""

    @staticmethod
    def _now_utc() -> datetime:
        return datetime.now(tz=UTC).astimezone(UTC).replace(tzinfo=UTC)

    @staticmethod
    def _recency_score(now: datetime, ts: datetime, half_life_hours: float) -> float:
        if not half_life_hours or half_life_hours <= 0:
            return 1.0
        age_sec = (now - ts).total_seconds()
        if age_sec < 0:
            age_sec = 0.0
        age_h = age_sec / 3600.0
        return 0.5 ** (age_h / float(half_life_hours))

    @classmethod
    def rank(
        cls,
        events: Iterable[dict[str, Any]],
        score_fn: Callable[[dict[str, Any]], float | None] | None = None,
        now: datetime | None = None,
        config: RankConfig | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        cfg = config or RankConfig()
        now_dt = _C1._coerce_naive_utc(now or cls._now_utc())
        session_weights = cfg.session_weights or {}

        scored: list[tuple[float, datetime, dict[str, Any], float]] = []
        for ev in events:
            ts_any = ev.get("ts") if "ts" in ev else ev.get("timestamp")
            if ts_any is None:
                continue
            dt = _C1._parse_ts(ts_any)
            if dt is None:
                continue

            base = 0.0
            if score_fn is not None:
                try:
                    s = score_fn(ev)
                    if s is not None:
                        base = float(s)
                except Exception:
                    base = 0.0

            r = cls._recency_score(now_dt, dt, cfg.half_life_hours)

            sid = str(ev.get("sid")) if ev.get("sid") is not None else None
            mult = 1.0
            if sid and sid in session_weights:
                with suppress(Exception):
                    mult *= float(session_weights[sid])
            if cfg.current_session and sid == cfg.current_session:
                mult *= 1.0 + float(cfg.current_session_boost)

            final = (base + cfg.recency_weight * r) * mult

            ev_out = ev
            if cfg.annotate:
                ev_out.setdefault("rank_score", final)
                ev_out.setdefault("rank_recency", r)

            scored.append((final, dt, ev_out, r))

        # dedup
        if cfg.dedup_by:
            key_fields = tuple(cfg.dedup_by)
            reduced: dict[tuple[Any, ...], tuple[float, datetime, dict[str, Any], float]] = {}
            for tup in scored:
                k = tuple(tup[2].get(f) for f in key_fields)
                if k not in reduced:
                    reduced[k] = tup
                else:
                    if cfg.dedup_strategy == "best":
                        old = reduced[k]
                        if (tup[0] > old[0]) or (math.isclose(tup[0], old[0]) and tup[1] > old[1]):
                            reduced[k] = tup
                    elif cfg.dedup_strategy == "last":
                        reduced[k] = tup
                    # "first"면 기존 유지
            scored = list(reduced.values())

        # 점수 desc, ts desc
        scored.sort(key=lambda t: (t[0], t[1]), reverse=True)

        if limit is not None and limit >= 0:
            scored = scored[:limit]

        return [t[2] for t in scored]
