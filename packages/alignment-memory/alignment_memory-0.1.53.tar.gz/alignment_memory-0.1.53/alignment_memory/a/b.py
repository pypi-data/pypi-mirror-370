from __future__ import annotations

import os
import re
from collections.abc import Callable, Iterable
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from typing import Any

Event = dict[str, Any]

# ---------- TZ helpers ----------
_DEF_LOCAL_TZ: tzinfo | None = None  # lazy init


def _parse_offset(s: str) -> tzinfo | None:
    m = re.fullmatch(r"([+-])(\d{2}):(\d{2})", s or "")
    if not m:
        return None
    sign = 1 if m.group(1) == "+" else -1
    hh = int(m.group(2))
    mm = int(m.group(3))
    return timezone(sign * timedelta(hours=hh, minutes=mm))


def _get_local_tzinfo(explicit: str | None) -> tzinfo:
    """
    tz 선택 우선순위:
      1) explicit == 'utc' → UTC
      2) explicit == '+HH:MM' 형태 → 해당 오프셋
      3) env AB_TZ_OFFSET → '+HH:MM' 형태
      4) 시스템 로컬 tz
    """
    if explicit:
        if explicit.lower() == "utc":
            return UTC
        tz = _parse_offset(explicit)
        if tz is not None:
            return tz

    env_tz = os.environ.get("AB_TZ_OFFSET")
    if env_tz:
        tz = _parse_offset(env_tz)
        if tz is not None:
            return tz

    global _DEF_LOCAL_TZ
    if _DEF_LOCAL_TZ is None:
        _DEF_LOCAL_TZ = datetime.now().astimezone().tzinfo or UTC

    assert _DEF_LOCAL_TZ is not None
    return _DEF_LOCAL_TZ


def _is_day_string(s: str) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s or ""))


def _to_aware_utc(dt: datetime, local_tz: tzinfo) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=local_tz)
    return dt.astimezone(UTC)


def _parse_event_ts_to_utc(ts: Any, local_tz: tzinfo) -> datetime | None:
    """
    이벤트 ts를 UTC aware로 변환:
      - int/float → epoch seconds (UTC)
      - datetime → tz 보정 후 UTC
      - str:
          - epoch digits → UTC
          - ...Z → UTC
          - tz offset 포함 → 해당 오프셋에서 UTC
          - naive → local_tz로 해석 후 UTC
    실패 시 None
    """
    if ts is None:
        return None
    if isinstance(ts, int | float):
        try:
            return datetime.fromtimestamp(float(ts), tz=UTC)
        except Exception:
            return None
    if isinstance(ts, datetime):
        try:
            return _to_aware_utc(ts, local_tz)
        except Exception:
            return None

    # 문자열 처리
    s = str(ts).strip()
    if not s:
        return None
    if s.isdigit() or (s[0] in "+-" and s[1:].isdigit()):
        try:
            return datetime.fromtimestamp(float(s), tz=UTC)
        except Exception:
            return None
    try:
        if s.endswith("Z"):
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=local_tz)
        return dt.astimezone(UTC)
    except Exception:
        return None


def _expand_day_to_utc_window(day: str, local_tz: tzinfo) -> tuple[datetime, datetime]:
    start_local = datetime.fromisoformat(day + "T00:00:00").replace(tzinfo=local_tz)
    end_local = datetime.fromisoformat(day + "T23:59:59.999999").replace(tzinfo=local_tz)
    return (start_local.astimezone(UTC), end_local.astimezone(UTC))


def _build_text_predicate(
    pattern: str | None,
    mode: str,
    ignore_case: bool,
) -> Callable[[str], bool]:
    if not pattern:
        return lambda _s: True
    if mode == "exact":
        if ignore_case:
            p = pattern.casefold()
            return lambda s: (str(s).casefold() == p)
        return lambda s: (str(s) == pattern)
    if mode == "regex":
        flags = re.IGNORECASE if ignore_case else 0
        rx = re.compile(pattern, flags)
        return lambda s: rx.search(str(s)) is not None
    # substr
    if ignore_case:
        p = pattern.casefold()

        def _pred(s: str) -> bool:
            s = str(s)
            if p in s.casefold():
                return True
            # 폴딩 이슈 대비
            try:
                return re.search(re.escape(pattern), s, flags=re.IGNORECASE) is not None
            except Exception:
                return False

        return _pred
    return lambda s: (pattern in str(s))


# ---------- main ----------
class Class1:
    # --- Class3 호환용 내부 유틸(shim) ---
    @staticmethod
    def _coerce_naive_utc(dt: datetime) -> datetime:
        """tz-aware면 UTC로 바꾸고 naive로, tz-naive면 그대로."""
        if dt.tzinfo is not None:
            return dt.astimezone(UTC).replace(tzinfo=None)
        return dt

    @staticmethod
    def _parse_ts(value: str | int | float | datetime) -> datetime | None:
        """값을 naive UTC datetime으로 파싱(Class3에서 사용)."""
        dt = _parse_event_ts_to_utc(value, _get_local_tzinfo("utc"))
        if dt is None:
            return None
        return dt.replace(tzinfo=None)

    @staticmethod
    def filter_events(
        events: Iterable[Event],
        *,
        text: str | None = None,
        text_mode: str = "substr",  # 'substr' | 'regex' | 'exact'
        ignore_case: bool = False,
        speaker: str | None = None,
        speakers: list[str] | None = None,
        since: str | None = None,
        until: str | None = None,
        sort: str = "asc",  # 'asc' | 'desc'
        sort_by: str = "ts",  # 'ts' | 'score'
        offset: int = 0,
        limit: int = 0,
        score_fn: Callable[[Event], float | None] | None = None,
        pre_filter: Callable[[Event], Event | None] | None = None,
        post_filter: Callable[[Event], Event] | None = None,
        tz: str | None = None,  # 'local' | 'utc' | '+09:00' 등
        **_ignore_kwargs,
    ) -> list[Event]:
        """선택/정렬/페이징 적용된 새로운 이벤트 사본 반환(원본 불변)."""
        local_tz = _get_local_tzinfo(None if (tz or "local") == "local" else tz)

        text_ok = _build_text_predicate(text, text_mode, ignore_case)
        speakers_set = set(speakers) if speakers else None

        since_utc = until_utc = None
        target_day: str | None = None
        if since and _is_day_string(since):
            since_utc, _ = _expand_day_to_utc_window(since, local_tz)
            target_day = since
        else:
            since_utc = _parse_event_ts_to_utc(since, local_tz) if since else None
        if until and _is_day_string(until):
            _, until_utc = _expand_day_to_utc_window(until, local_tz)
            target_day = until if (target_day is None) else target_day
        else:
            until_utc = _parse_event_ts_to_utc(until, local_tz) if until else None

        day_match: str | None = None
        if target_day and _is_day_string(since or "") and _is_day_string(until or "") and (since == until):
            day_match = target_day  # 'YYYY-MM-DD'

        def _in_range(ts_val: Any) -> bool:
            dt = _parse_event_ts_to_utc(ts_val, local_tz)

            # 1) since/until 미지정: 유효한 타임스탬프만 포함
            if not (since_utc or until_utc):
                return dt is not None

            # 2) 범위 지정된 경우: 기존 범위 체크
            if dt is not None:
                if since_utc and dt < since_utc:
                    return False
                return not (until_utc and dt > until_utc)

            # 3) 파싱 실패: day-range 지정 시 문자열 날짜 보정
            if day_match and isinstance(ts_val, str) and len(ts_val) >= 10:
                return ts_val[:10] == day_match
            return False

        picked: list[Event] = []
        for ev in events:
            src = ev
            if pre_filter:
                tmp = pre_filter(src)
                if tmp is None:
                    continue
                cur = dict(tmp)
            else:
                cur = dict(src)

            sp = str(cur.get("speaker", "") or "")
            if speaker and sp != speaker:
                continue
            if speakers_set is not None and sp not in speakers_set:
                continue

            if not _in_range(cur.get("ts", "")):
                continue

            txt = str(cur.get("text", "") or "")
            if not text_ok(txt):
                continue

            if post_filter:
                cur = dict(post_filter(cur))

            picked.append(cur)

        # 정렬
        rev = sort == "desc"
        if sort_by == "score" and score_fn is not None:
            scored: list[tuple[float, int, Event]] = []
            fallback: list[Event] = []
            for idx, e in enumerate(picked):
                try:
                    s = score_fn(e)
                except Exception:
                    s = None
                if s is None:
                    fallback.append(e)
                else:
                    scored.append((float(s), idx, e))
            scored.sort(key=lambda t: (t[0], t[1]), reverse=rev)

            def _ts_key(ev: Event) -> tuple[datetime]:
                dt = _parse_event_ts_to_utc(ev.get("ts", ""), local_tz)
                return (dt or datetime.min.replace(tzinfo=UTC),)

            fallback.sort(key=_ts_key, reverse=rev)
            ordered = [e for (_s, _i, e) in scored] + fallback
        else:

            def _ts_key(ev: Event) -> tuple[datetime]:
                dt = _parse_event_ts_to_utc(ev.get("ts", ""), local_tz)
                return (dt or datetime.min.replace(tzinfo=UTC),)

            ordered = sorted(picked, key=_ts_key, reverse=rev)

        if offset > 0:
            ordered = ordered[offset:]
        if limit and limit > 0 and len(ordered) > limit:
            ordered = ordered[:limit]

        return ordered
