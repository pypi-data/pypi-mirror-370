from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_ok(args):
    p = subprocess.run(
        [sys.executable, "-m", "alignment_memory.cli", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return p.stdout.strip()


def test_list_and_show(tmp_path: Path):
    data = tmp_path
    sid = run_ok(["new", "--data-dir", str(data)]).splitlines()[-1].strip()
    run_ok(["append", "--data-dir", str(data), "--id", sid, "--speaker", "user", "--content", "hello"])
    run_ok(
        [
            "append",
            "--data-dir",
            str(data),
            "--id",
            sid,
            "--speaker",
            "assistant",
            "--content",
            "world",
        ]
    )

    out_list = run_ok(["list", "--data-dir", str(data)])
    assert sid in out_list

    out_show = run_ok(["show", "--data-dir", str(data), "--id", sid])
    assert "# session:" in out_show
    assert "hello" in out_show and "world" in out_show
