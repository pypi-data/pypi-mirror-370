import subprocess
import sys

from alignment_memory.auth import oidc
from alignment_memory.idm import connectors
from alignment_memory.sign import api


def test_placeholders_exist():
    assert hasattr(oidc, "OIDCConfig")
    assert hasattr(connectors, "ldap_ping")
    assert hasattr(api, "RestSignClient")


def test_cli_stub_help():
    out = subprocess.run([sys.executable, "-m", "alignment_memory.cli", "-h"], capture_output=True, text=True)
    assert out.returncode == 0
    s = out.stdout
    assert "auth" in s and "idm" in s and "esign" in s
