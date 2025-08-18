from __future__ import annotations

import argparse
import json
import sys
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from alignment_memory.license import check_license

from .enterprise import add_enterprise_commands, handle_enterprise

# --- Optional integrations (존재하면 사용) ---
_Class1: object | None = None
try:
    from alignment_memory.a import Class1 as _ImportedClass1

    _Class1 = _ImportedClass1
except Exception:
    _Class1 = None

_Class3: object | None = None
_RankConfig: object | None = None
try:
    from alignment_memory.a.class3 import Class3 as _ImpClass3
    from alignment_memory.a.class3 import RankConfig as _ImpRankConfig

    _Class3, _RankConfig = _ImpClass3, _ImpRankConfig
except Exception:
    _Class3 = None
    _RankConfig = None


# ------------------------ 유틸 ------------------------
def _now_iso() -> str:
    return datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z"


def _parse_ts(s: str | None) -> str:
    if s is None or str(s).lower() == "now":
        return _now_iso()
    s = str(s).strip()
    if s.isdigit() or (s and s[0] in "+-" and s[1:].isdigit()):
        dt = datetime.fromtimestamp(float(s), tz=UTC).replace(tzinfo=None)
        return dt.isoformat() + "Z"
    if s.endswith("Z"):
        return s
    try:
        datetime.fromisoformat(s.replace("Z", "+00:00"))
        return s
    except Exception:
        return _now_iso()


def _sessions_dir(root: Path) -> Path:
    p = root / "sessions"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _session_file(root: Path, sid: str | None) -> Path:
    return _sessions_dir(root) / f"{str(sid)}.jsonl"


def _load_events(root: Path, sid: str | None = None) -> list[dict[str, Any]]:
    evs: list[dict[str, Any]] = []
    sdir = _sessions_dir(root)
    files = [_session_file(root, sid)] if sid else sorted(sdir.glob("*.jsonl"))
    for f in files:
        if not f.exists():
            continue
        with f.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                with suppress(Exception):
                    evs.append(json.loads(line))
    return evs


def _norm_sid(s: str | None) -> str | None:
    return None if s is None else str(s).strip()


def _guess_text(obj: dict) -> str | None:
    for k in ("text", "content", "message", "line"):
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return None


def _iter_import_lines(path: Path, default_speaker: str, default_ts: str | None):
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as fh:
            for raw in fh:
                s = raw.strip()
                if not s:
                    continue
                try:
                    x = json.loads(s)
                    if isinstance(x, dict):
                        text = _guess_text(x) or ""
                        if not text:
                            continue
                        speaker = str(x.get("speaker", default_speaker))
                        ts = _parse_ts(x.get("ts")) if x.get("ts") else (default_ts or _now_iso())
                        yield {"speaker": speaker, "text": text, "ts": ts}
                    elif isinstance(x, str) and x.strip():
                        yield {
                            "speaker": default_speaker,
                            "text": x.strip(),
                            "ts": default_ts or _now_iso(),
                        }
                except Exception:
                    # JSON 파싱 실패 시 한 줄 텍스트로 취급
                    yield {"speaker": default_speaker, "text": s, "ts": default_ts or _now_iso()}
    else:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                t = line.strip()
                if not t:
                    continue
                yield {"speaker": default_speaker, "text": t, "ts": default_ts or _now_iso()}


# ------------------------ 커맨드 구현 ------------------------
def cmd_smoke(args: argparse.Namespace) -> int:
    print("SMOKE")
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    import uuid

    sid = uuid.uuid4().hex[:12]
    _session_file(Path(args.data_dir), sid).touch()
    print(sid)
    return 0


def cmd_append(args: argparse.Namespace) -> int:
    root = Path(args.data_dir)
    sid = _norm_sid(args.sid)
    ev = {"sid": sid, "ts": _parse_ts(args.ts), "speaker": args.speaker, "text": args.text}
    fp = _session_file(root, sid)
    fp.parent.mkdir(parents=True, exist_ok=True)
    with fp.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, ensure_ascii=False) + "\n")
    print("OK")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    root = Path(args.data_dir)
    sid = _norm_sid(getattr(args, "sid", None)) if getattr(args, "sid", None) else None
    generated_new = False
    if not sid:
        import uuid

        sid = uuid.uuid4().hex[:12]
        generated_new = True

    sfile = _session_file(root, sid)
    sfile.parent.mkdir(parents=True, exist_ok=True)

    sources: list[Path] = []
    if getattr(args, "paths", None):
        for p in args.paths:
            pp = Path(p)
            if pp.exists() and pp.is_file():
                sources.append(pp)
    if getattr(args, "globpat", None):
        for pp in Path().glob(args.globpat):
            if pp.is_file():
                sources.append(pp)

    sources = list(dict.fromkeys(sources))

    if not sources:
        print("ERROR: no input files (use --paths or --glob)", file=sys.stderr)
        return 2

    default_ts = _parse_ts(args.ts) if getattr(args, "ts", None) else None

    n = 0
    with sfile.open("a", encoding="utf-8") as out:
        for src in sources:
            for ev in _iter_import_lines(src, args.speaker, default_ts):
                ev["sid"] = sid
                out.write(json.dumps(ev, ensure_ascii=False) + "\n")
                n += 1

    if getattr(args, "format", "lines") == "json" or getattr(args, "json", False):
        print(json.dumps({"sid": sid, "imported": n, "files": [str(s) for s in sources]}, ensure_ascii=False))
    else:
        if generated_new:
            print(f"# session: {sid}")
        print(f"imported {n}")
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    root = Path(args.data_dir)
    sid = _norm_sid(getattr(args, "sid", None)) if getattr(args, "sid", None) else None
    if not sid:
        print("ERROR: --sid/--id is required", file=sys.stderr)
        return 2
    sfile = _session_file(root, sid)
    expfile = root / "exports" / f"{sid}.txt"
    any_deleted = False
    if sfile.exists():
        sfile.unlink()
        any_deleted = True
        print(f"# deleted: {sfile}")
    else:
        print("# not found: session file", file=sys.stderr)
    if getattr(args, "with_export", False) and expfile.exists():
        expfile.unlink()
        print(f"# deleted: {expfile}")
    print("OK" if any_deleted else "NOOP")
    return 0 if any_deleted else 1


def cmd_purge(args: argparse.Namespace) -> int:
    root = Path(args.data_dir)
    sdir = _sessions_dir(root)
    removed = 0
    for f in sdir.glob("*.jsonl"):
        f.unlink()
        removed += 1
    if getattr(args, "with_exports", False):
        edir = root / "exports"
        if edir.exists():
            for f in edir.glob("*.txt"):
                with suppress(Exception):
                    f.unlink()
    if getattr(args, "format", "lines") == "json" or getattr(args, "json", False):
        print(json.dumps({"removed": removed}, ensure_ascii=False))
    else:
        print(f"removed {removed}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    root = Path(args.data_dir)
    sid = _norm_sid(getattr(args, "sid", None))
    if not sid:
        print("ERROR: --sid/--id is required", file=sys.stderr)
        return 2
    evs = _load_events(root, sid)
    total = len(evs)
    by_speaker: dict[str, int] = {}
    for ev in evs:
        sp = ev.get("speaker") or ""
        by_speaker[sp] = by_speaker.get(sp, 0) + 1
    first_ts = evs[0]["ts"] if evs else None
    last_ts = evs[-1]["ts"] if evs else None
    payload = {
        "sid": sid,
        "total": total,
        "by_speaker": by_speaker,
        "first_ts": first_ts,
        "last_ts": last_ts,
    }
    if getattr(args, "format", None) == "json" or getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(f"# session: {sid}")
        print(f"total {total}")
        for sp, c in sorted(by_speaker.items()):
            print(f"{sp or '-'} {c}")
        if first_ts:
            print(f"first {first_ts}")
        if last_ts:
            print(f"last {last_ts}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    """
    검색 편의/품질:
      - --since / --until : ISO8601 또는 epoch(초). 경계 포함.
      - --speaker         : 발화자 필터(정확 일치)
      - --ignore-case     : 대소문자 무시 텍스트 검색
      - --limit N         : 필터 후 '최근 N개'만 출력(시간 오름차순으로 보여줌)
      - --tz              : 날짜만 주어졌을 때 해석할 기준 타임존(예: Asia/Seoul, UTC, +09:00)
    """
    root = Path(args.data_dir)
    args.sid = _norm_sid(getattr(args, "sid", None))
    evs = _load_events(root, args.sid)
    text = args.text or ""

    since = _parse_ts(args.since) if getattr(args, "since", None) else None
    until = _parse_ts(args.until) if getattr(args, "until", None) else None

    if _Class1:
        C1 = cast(Any, _Class1)
        evs = C1.filter_events(
            evs,
            text=text,
            ignore_case=args.ignore_case,
            since=since,
            until=until,
            speaker=args.speaker,
            sort="asc",
            tz=getattr(args, "tz", None),
        )
    else:
        t = text or ""
        t_cmp = t.lower() if args.ignore_case else t

        def _in_range(ts: str, lo: str | None, hi: str | None) -> bool:
            if not ts:
                return False
            return (lo is None or ts >= lo) and (hi is None or ts <= hi)

        def _match_text(ev):
            if not t:
                return True
            hay = ev.get("text", "")
            hay = hay.lower() if args.ignore_case else hay
            return t_cmp in hay

        def _match_speaker(ev):
            if not args.speaker:
                return True
            return (ev.get("speaker") or "") == args.speaker

        evs = [ev for ev in evs if _in_range(ev.get("ts", ""), since, until) and _match_speaker(ev) and _match_text(ev)]
        evs.sort(key=lambda ev: ev.get("ts", ""))  # 시간 오름차순

    if getattr(args, "limit", 0):
        n = max(0, int(args.limit))
        if n > 0 and len(evs) > n:
            evs = evs[-n:]

    if args.format == "json" or args.json:
        print(json.dumps(evs, ensure_ascii=False))
    else:
        for ev in evs:
            print(f"{ev.get('ts', '')} {ev.get('speaker', '')}: {ev.get('text', '')}")
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    root = Path(args.data_dir)
    args.sid = _norm_sid(args.sid)
    evs = _load_events(root, args.sid)
    lim = args.limit or 5
    top = evs
    if _Class3 and _RankConfig:
        RC = cast(Any, _RankConfig)
        C3 = cast(Any, _Class3)
        cfg = RC(annotate=False, recency_weight=1.0)
        top = C3.rank(evs, score_fn=None, now=None, config=cfg, limit=lim)
    else:
        top = evs[-lim:]
    top = sorted(top, key=lambda ev: ev.get("ts", ""))

    if args.format == "json" or args.json:
        items = [
            {
                "n": i + 1,
                "ts": ev.get("ts", ""),
                "speaker": ev.get("speaker", ""),
                "content": ev.get("text", ""),
            }
            for i, ev in enumerate(top)
        ]
        print(json.dumps(items, ensure_ascii=False))
    else:
        for ev in top:
            print(ev.get("text", ""))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    root = Path(args.data_dir)
    args.sid = _norm_sid(args.sid)
    evs = _load_events(root, args.sid)
    out_dir = root / "exports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.sid}.txt"
    with out_path.open("w", encoding="utf-8") as fh:
        for ev in evs:
            fh.write(f"{ev.get('ts', '')} {ev.get('speaker', '')}: {ev.get('text', '')}\n")
    print(str(out_path))
    return 0


def _summarize_session_file(fp: Path) -> dict[str, Any]:
    """list --format json 용 세션 요약(빠르게 count/first/last)"""
    sid = fp.stem
    count = 0
    first_ts: str | None = None
    last_ts: str | None = None
    try:
        with fp.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                ts = ev.get("ts")
                if ts:
                    if first_ts is None:
                        first_ts = ts
                    last_ts = ts
                count += 1
    except Exception:
        pass
    return {"sid": sid, "count": count, "first_ts": first_ts, "last_ts": last_ts}


def cmd_list(args: argparse.Namespace) -> int:
    sdir = _sessions_dir(Path(args.data_dir))
    files = sorted(sdir.glob("*.jsonl"))

    # --count : 세션 개수만
    if getattr(args, "count_only", False):
        print(len(files))
        return 0

    if getattr(args, "format", "lines") == "json" or getattr(args, "json", False):
        payload = [_summarize_session_file(f) for f in files]
        print(json.dumps(payload, ensure_ascii=False, indent=None))
    else:
        for f in files:
            print(f.stem)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    root = Path(args.data_dir)
    args.sid = _norm_sid(args.sid)
    evs = _load_events(root, args.sid)
    last_k = max(0, int(getattr(args, "last", 0) or 0))
    if last_k > 0 and len(evs) > last_k:
        evs = evs[-last_k:]
    # 테스트 기대에 맞춘 헤더
    print(f"# session: {args.sid}")

    if getattr(args, "format", "lines") == "json" or getattr(args, "json", False):
        print(json.dumps(evs, ensure_ascii=False))
    else:
        for ev in evs:
            print(f"{ev.get('ts', '')} {ev.get('speaker', '')}: {ev.get('text', '')}")
    return 0


# NEW: last-id --------------------------------------------------------------
def cmd_last_id(args: argparse.Namespace) -> int:
    """가장 최근 세션 ID 출력 (기본: last_ts 기준)."""
    root = Path(args.data_dir)
    sdir = _sessions_dir(root)
    files = sorted(sdir.glob("*.jsonl"))
    if not files:
        if args.format == "json":
            print(json.dumps({"sid": None}, ensure_ascii=False))
        else:
            print("")
        return 1

    items = [(_summarize_session_file(f), f) for f in files]
    if args.nonempty:
        items = [(s, f) for (s, f) in items if (s.get("count") or 0) > 0]
        if not items:
            if args.format == "json":
                print(json.dumps({"sid": None}, ensure_ascii=False))
            else:
                print("")
            return 1

    def _key(pair):
        s, f = pair
        ts = s.get("last_ts")
        return (ts or "", f.stat().st_mtime)

    latest_summary, _ = max(items, key=_key)
    sid = latest_summary["sid"]

    if args.format == "json":
        print(json.dumps({"sid": sid}, ensure_ascii=False))
    else:
        print(sid)
    return 0


# ------------------------ 엔트리포인트 ------------------------
def main(argv: list[str] | None = None) -> int:
    check_license()  # -m 경로에서도 라이선스 체크 보장

    p = argparse.ArgumentParser(prog="alignment_memory.cli")
    sp = p.add_subparsers(dest="cmd", required=True)

    # 엔터프라이즈 커맨드 등록 (먼저 등록해도 무방)
    add_enterprise_commands(sp)

    # smoke
    sp_smoke = sp.add_parser("smoke")
    sp_smoke.add_argument("--data-dir", default=str(Path.cwd()))
    sp_smoke.set_defaults(func=cmd_smoke)

    # new
    sp_new = sp.add_parser("new")
    sp_new.add_argument("--data-dir", default=str(Path.cwd()))
    sp_new.set_defaults(func=cmd_new)

    # append
    sp_append = sp.add_parser("append")
    sp_append.add_argument("--data-dir", default=str(Path.cwd()))
    g_sid = sp_append.add_mutually_exclusive_group(required=True)
    g_sid.add_argument("--sid", dest="sid")
    g_sid.add_argument("--id", dest="sid", help="alias of --sid")
    sp_append.add_argument("--speaker", required=True)
    g_txt = sp_append.add_mutually_exclusive_group(required=True)
    g_txt.add_argument("--text", dest="text")
    g_txt.add_argument("--content", dest="text", help="alias of --text")
    sp_append.add_argument("--ts", default=None)
    sp_append.set_defaults(func=cmd_append)

    # import
    sp_imp = sp.add_parser("import")
    sp_imp.add_argument("--data-dir", default=str(Path.cwd()))
    sp_imp.add_argument("--sid", "--id", dest="sid")
    sp_imp.add_argument("--speaker", default="user")
    sp_imp.add_argument("--ts")
    sp_imp.add_argument("--paths", nargs="+", help="Files to import")
    sp_imp.add_argument("--glob", dest="globpat", help="Glob pattern (e.g., *.txt)")
    sp_imp.add_argument("--json", action="store_true")
    sp_imp.add_argument("--format", choices=["json", "lines"], default="lines")
    sp_imp.set_defaults(func=cmd_import)

    # delete
    sp_del = sp.add_parser("delete")
    sp_del.add_argument("--data-dir", default=str(Path.cwd()))
    sp_del.add_argument("--sid", "--id", dest="sid", required=True)
    sp_del.add_argument("--with-export", action="store_true")
    sp_del.set_defaults(func=cmd_delete)

    # purge
    sp_purge = sp.add_parser("purge")
    sp_purge.add_argument("--data-dir", default=str(Path.cwd()))
    sp_purge.add_argument("--with-exports", action="store_true")
    sp_purge.add_argument("--json", action="store_true")
    sp_purge.add_argument("--format", choices=["json", "lines"], default="lines")
    sp_purge.set_defaults(func=cmd_purge)

    # stats
    sp_stats = sp.add_parser("stats")
    sp_stats.add_argument("--data-dir", default=str(Path.cwd()))
    sp_stats.add_argument("--sid", "--id", dest="sid", required=True)
    sp_stats.add_argument("--json", action="store_true")
    sp_stats.add_argument("--format", choices=["json", "lines"], default="lines")
    sp_stats.set_defaults(func=cmd_stats)

    # search
    sp_search = sp.add_parser("search")
    sp_search.add_argument("--data-dir", default=str(Path.cwd()))
    g_sid2 = sp_search.add_mutually_exclusive_group(required=False)
    g_sid2.add_argument("--sid", dest="sid")
    g_sid2.add_argument("--id", dest="sid", help="alias of --sid")
    g_q = sp_search.add_mutually_exclusive_group(required=False)
    g_q.add_argument("--text", dest="text")
    g_q.add_argument("--query", dest="text", help="alias of --text")
    sp_search.add_argument("--ignore-case", action="store_true", dest="ignore_case")
    sp_search.add_argument("--since")
    sp_search.add_argument("--until")
    sp_search.add_argument("--speaker")
    sp_search.add_argument("--limit", type=int, default=0, help="return last-N after filtering")
    sp_search.add_argument("--tz")  # 대비용
    sp_search.add_argument("--json", action="store_true")
    sp_search.add_argument("--format", choices=["json", "lines"], default="lines")
    sp_search.set_defaults(func=cmd_search)

    # summarize
    sp_sum = sp.add_parser("summarize")
    sp_sum.add_argument("--data-dir", default=str(Path.cwd()))
    g_sid3 = sp_sum.add_mutually_exclusive_group(required=True)
    g_sid3.add_argument("--sid", dest="sid")
    g_sid3.add_argument("--id", dest="sid", help="alias of --sid")
    sp_sum.add_argument("--limit", type=int, default=5)
    sp_sum.add_argument("--last-k", dest="limit", type=int, help="alias of --limit")
    sp_sum.add_argument("--tz")  # 대비용
    sp_sum.add_argument("--json", action="store_true")
    sp_sum.add_argument("--format", choices=["json", "lines"], default="lines")
    sp_sum.set_defaults(func=cmd_summarize)

    # export
    sp_exp = sp.add_parser("export")
    sp_exp.add_argument("--data-dir", default=str(Path.cwd()))
    g_sid4 = sp_exp.add_mutually_exclusive_group(required=True)
    g_sid4.add_argument("--sid", dest="sid")
    g_sid4.add_argument("--id", dest="sid", help="alias of --sid")
    sp_exp.set_defaults(func=cmd_export)

    # list
    sp_ls = sp.add_parser("list")
    sp_ls.add_argument("--data-dir", default=str(Path.cwd()))
    sp_ls.add_argument("--count", action="store_true", dest="count_only", help="print only the number of sessions")
    sp_ls.add_argument("--json", action="store_true")
    sp_ls.add_argument("--format", choices=["json", "lines"], default="lines")
    sp_ls.set_defaults(func=cmd_list)

    # show
    sp_show = sp.add_parser("show")
    sp_show.add_argument("--data-dir", default=str(Path.cwd()))
    g_sid5 = sp_show.add_mutually_exclusive_group(required=True)
    g_sid5.add_argument("--sid", dest="sid")
    g_sid5.add_argument("--id", dest="sid", help="alias of --sid")
    sp_show.add_argument("--last", type=int, default=0, help="show last K events (0 = all)")
    sp_show.add_argument("--last-k", dest="last", type=int, help="alias of --last")
    sp_show.add_argument("--json", action="store_true")
    sp_show.add_argument("--format", choices=["json", "lines"], default="lines")
    sp_show.set_defaults(func=cmd_show)

    # NEW: last-id
    sp_last = sp.add_parser("last-id")
    sp_last.add_argument("--data-dir", default=str(Path.cwd()))
    sp_last.add_argument("--nonempty", action="store_true", help="이벤트가 있는 세션만 고려")
    sp_last.add_argument("--format", choices=["json", "lines"], default="lines")
    sp_last.set_defaults(func=cmd_last_id)

    args = p.parse_args(argv)

    # 먼저 엔터프라이즈 서브커맨드 처리 (엔터프라이즈 커맨드는 func가 없음)
    if handle_enterprise(args):
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
