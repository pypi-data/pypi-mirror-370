# alignment_memory/cli/cli.py
from __future__ import annotations

from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """
    Thin wrapper: delegate to alignment_memory.cli.__main__.main
    so there's a single source of truth for CLI behavior.
    """
    # Local import to avoid import cycles on type checkers
    from alignment_memory.cli.__main__ import main as _main

    # argparse expects list[str] or None
    return _main(list(argv) if argv is not None else None)


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
