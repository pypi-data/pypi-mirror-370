from __future__ import annotations

from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from typing import Any


def add_class1_args(p: ArgumentParser) -> ArgumentParser:
    p.add_argument("--text", type=str, default=None)
    p.add_argument("--text-mode", choices=["contains", "regex", "exact"], default="contains")
    p.add_argument("--ignore-case", action="store_true")
    p.add_argument("--since", type=str, default=None)  # YYYY-MM-DD or ISO8601
    p.add_argument("--until", type=str, default=None)
    p.add_argument("--speaker", type=str, default=None)
    p.add_argument("--speakers", type=str, default=None, help="Comma-separated allowlist")
    p.add_argument("--sort", choices=[None, "asc", "desc", "ASC", "DESC"], default=None)
    p.add_argument("--sort-by", choices=["ts", "score"], default="ts")
    p.add_argument("--offset", type=int, default=0)
    p.add_argument("--limit", type=int, default=None)
    return p


def _normalize_sort(v: str | None) -> str | None:
    if v is None:
        return None
    v = str(v).lower()
    return v if v in ("asc", "desc") else None


def kwargs_from_ns(ns: Namespace) -> dict[str, Any]:
    speakers: str | None = getattr(ns, "speakers", None)
    sp_list: Sequence[str] | None = None
    if speakers:
        sp_list = [s for s in (x.strip() for x in speakers.split(",")) if s]

    return {
        "text": getattr(ns, "text", None),
        "text_mode": getattr(ns, "text_mode", "contains"),
        "ignore_case": bool(getattr(ns, "ignore_case", False)),
        "since": getattr(ns, "since", None),
        "until": getattr(ns, "until", None),
        "speaker": getattr(ns, "speaker", None),
        "speakers": sp_list,
        "sort": _normalize_sort(getattr(ns, "sort", None)),
        "sort_by": getattr(ns, "sort_by", "ts"),
        "offset": int(getattr(ns, "offset", 0) or 0),
        "limit": getattr(ns, "limit", None),
    }
