import os
import subprocess
import sys


def _run_cli(tmp_dir, extra_env):
    env = {**os.environ, **extra_env}
    cmd = [sys.executable, "-m", "alignment_memory.cli", "smoke", "--data-dir", str(tmp_dir)]
    return subprocess.run(cmd, env=env, capture_output=True, text=True)


def test_restricted_warn(tmp_path):
    r = _run_cli(tmp_path, {"AB_LICENSE_MODE": "restricted", "AB_LICENSE_ENFORCE": "0"})
    # 경고만, 정상 종료
    assert r.returncode == 0
    assert "restricted mode" in (r.stderr or "")


def test_restricted_enforced(tmp_path):
    r = _run_cli(tmp_path, {"AB_LICENSE_MODE": "restricted", "AB_LICENSE_ENFORCE": "1"})
    # 실행 차단, 종료 코드 2
    assert r.returncode == 2
    assert "enforced" in (r.stderr or "")
