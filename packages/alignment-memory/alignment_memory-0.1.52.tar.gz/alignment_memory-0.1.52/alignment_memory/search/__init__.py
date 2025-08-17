from __future__ import annotations

from typing import Any, cast

from alignment_memory.memory import load


def search(session_id: str, query: str) -> tuple[bool, list[dict[str, Any]] | str]:
    ok, payload_or_err = load(session_id)
    if not ok:
        return False, str(payload_or_err)

    # mypy: payload_or_err is Union[...] here; narrow to a dict-like
    payload = cast(dict, payload_or_err)
    msgs = payload.get("messages", [])
    if not isinstance(msgs, list) or not query:
        return True, []

    out: list[dict[str, Any]] = []
    for m in msgs:
        if not isinstance(m, dict):
            continue
        text = str(m.get("content", ""))
        if query in text:
            out.append({"ts": m.get("ts", ""), "snippet": text[:80]})
    return True, out
