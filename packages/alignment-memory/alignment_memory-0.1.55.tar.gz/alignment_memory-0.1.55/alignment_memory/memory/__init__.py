from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypedDict, cast

BASE_DIR = Path(__file__).resolve().parent / "sessions"
BASE_DIR.mkdir(parents=True, exist_ok=True)


class SessionPayload(TypedDict):
    id: str
    messages: list[dict[str, Any]]


def _path(session_id: str) -> Path:
    return BASE_DIR / f"{session_id}.json"


def load(session_id: str) -> tuple[bool, SessionPayload | str]:
    fp = _path(session_id)
    if not fp.exists():
        return False, "not found"
    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"read error: {e}"
    if not isinstance(obj, dict):
        return False, "invalid file"
    messages = obj.get("messages", [])
    if not isinstance(messages, list):
        messages = []
    payload: SessionPayload = {
        "id": str(obj.get("id", session_id)),
        "messages": messages,
    }
    return True, payload


def save(payload: SessionPayload) -> tuple[bool, str]:
    sid = payload.get("id", "")
    if not sid:
        return False, "missing id"
    fp = _path(sid)
    data = {"id": sid, "messages": payload.get("messages", [])}
    try:
        fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True, str(fp)
    except Exception as e:
        return False, str(e)


def append(session_id: str, msg: dict[str, Any]) -> tuple[bool, str]:
    ok, res = load(session_id)
    payload: SessionPayload = cast(SessionPayload, res) if ok else {"id": session_id, "messages": []}
    messages = list(payload.get("messages", []))
    messages.append(msg)
    payload["messages"] = messages
    return save(payload)
