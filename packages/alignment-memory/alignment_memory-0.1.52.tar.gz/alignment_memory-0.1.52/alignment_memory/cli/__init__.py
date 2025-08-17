# alignment_memory/cli/__init__.py
from alignment_memory.license import check_license


def main(argv=None):
    check_license()
    from .__main__ import main as _main  # 지연 임포트 👍

    return _main(argv)


__all__ = ["main"]
