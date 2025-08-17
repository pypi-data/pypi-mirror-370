from __future__ import annotations

from contextlib import suppress

from .b import Class1  # noqa: F401

# 선택: Class3, RankConfig (있으면 노출, 없으면 조용히 무시)
with suppress(Exception):
    from .class3 import Class3, RankConfig  # noqa: F401
