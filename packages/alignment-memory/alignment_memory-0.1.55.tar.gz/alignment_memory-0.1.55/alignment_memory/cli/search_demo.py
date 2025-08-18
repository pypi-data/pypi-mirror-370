from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Iterable
from typing import Any

from alignment_memory.a import Class1

from .class1_args import add_class1_args, kwargs_from_ns


def _iter_events(fp) -> Iterable[dict[str, Any]]:
    for line in fp:
        s = line.strip()
        if not s:
            continue
        try:
            yield json.loads(s)
        except Exception:
            continue


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="alm-search-demo", description="Class1 filter demo (JSONL)")
    ap.add_argument("--data-dir", type=str, default=os.environ.get("ALMEM_DIR"))
    ap.add_argument("--file", type=str, default="events.jsonl", help="events jsonl file name")
    ap.add_argument("--output", choices=["jsonl", "json"], default="jsonl")
    add_class1_args(ap)
    ns = ap.parse_args(argv)

    data_dir = ns.data_dir
    if not data_dir:
        print("ERROR: --data-dir is required (or set ALMEM_DIR).", file=sys.stderr)
        return 2
    path = os.path.join(data_dir, ns.file)
    if not os.path.exists(path):
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2

    with open(path, encoding="utf-8") as f:
        events = list(_iter_events(f))

    kwargs = kwargs_from_ns(ns)
    out = Class1.filter_events(events, **kwargs)

    if ns.output == "json":
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for ev in out:
            print(json.dumps(ev, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
