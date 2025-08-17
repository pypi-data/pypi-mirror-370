from __future__ import annotations

from pathlib import Path
from typing import Any

from alignment_memory.memory import load


def export(session_id: str, out_dir: str = "exports") -> tuple[bool, str]:
    """
    세션의 메시지를 텍스트로 내보내기.
    반환: (ok, path_or_error)
    """
    ok, data = load(session_id)
    if not ok or not isinstance(data, dict):
        return False, str(data)

    msgs: list[dict[str, Any]] = data.get("messages", []) or []
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)
    out_path = out_dir_p / f"{session_id}.txt"

    with out_path.open("w", encoding="utf-8") as fh:
        for ev in msgs:
            if not isinstance(ev, dict):
                continue
            ts = ev.get("ts", "")
            sp = ev.get("speaker", "")
            text = ev.get("text", ev.get("content", ""))
            fh.write(f"{ts} {sp}: {text}\n")

    return True, str(out_path)
