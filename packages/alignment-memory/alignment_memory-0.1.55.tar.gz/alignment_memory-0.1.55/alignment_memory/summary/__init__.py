from __future__ import annotations

from typing import cast

from alignment_memory.memory import load


def summarize(session_id: str) -> tuple[bool, str]:
    ok, payload_or_err = load(session_id)
    if not ok:
        return False, str(payload_or_err)

    # mypy: payload_or_err is Union[...] here; narrow to a dict-like
    payload = cast(dict, payload_or_err)
    msgs = payload.get("messages", [])
    if not isinstance(msgs, list) or not msgs:
        return True, ""

    texts: list[str] = []
    for m in msgs:
        if isinstance(m, dict):
            texts.append(str(m.get("content", "")))
        else:
            texts.append(str(m))
    return True, " ".join(texts[:5])
