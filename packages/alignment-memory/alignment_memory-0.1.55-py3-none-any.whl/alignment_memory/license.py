# alignment_memory/license.py
from __future__ import annotations

import os
import re
import sys

_CHECKED = False

_KEY_RE = re.compile(r"^AB-[A-Z0-9]{10,}$")  # 예: AB-1A2B3C4D5E...


def _is_valid_key(key: str | None) -> bool:
    if not key:
        return False
    return bool(_KEY_RE.fullmatch(key.strip()))


def check_license(exit_code: int | None = None) -> None:
    """
    ENV:
      AB_LICENSE_MODE     = full | restricted | auto(default)
      AB_LICENSE_ENFORCE  = 1/true/on 이면 restricted에서 종료
      AB_LICENSE_KEY      = "AB-..." 형식이면 full로 간주(auto일 때)

    종료코드:
      강제 차단(enforce)일 때만 종료. 기본 2(원하면 인자/ENV로 바꿔도 됨).
    """
    global _CHECKED
    if _CHECKED:
        return
    _CHECKED = True

    mode = (os.getenv("AB_LICENSE_MODE") or "auto").strip().lower()
    enforce_flag = (os.getenv("AB_LICENSE_ENFORCE") or "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    key = os.getenv("AB_LICENSE_KEY") or ""

    # auto 모드: 키가 유효하면 full, 아니면 restricted
    if mode == "auto":
        mode = "full" if _is_valid_key(key) else "restricted"

    # full 모드인데 키가 형식 불량인 경우는 restricted로 취급(보수적으로)
    if mode == "full" and not _is_valid_key(key):
        mode = "restricted"

    if mode == "restricted":
        if enforce_flag:
            code = 2 if exit_code is None else int(exit_code)
            print("[license] missing/invalid AB_LICENSE_KEY → restricted (enforced).", file=sys.stderr)
            sys.exit(code)
        else:
            print("[license] restricted mode (set AB_LICENSE_KEY for full).", file=sys.stderr)
    # mode == "full" 이면 아무 메시지 없이 통과
