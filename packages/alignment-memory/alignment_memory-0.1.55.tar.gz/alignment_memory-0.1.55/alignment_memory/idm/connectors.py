from __future__ import annotations

from typing import Any


def ldap_ping(host: str, port: int = 389, timeout: float = 1.0) -> bool:
    # Stub: ?? LDAP ??? ?? False
    _ = (host, port, timeout)
    return False


def scim_list(base_url: str, token: str, resource: str = "Users", limit: int = 10) -> list[dict[str, Any]]:
    # Stub: ?? SCIM ?? ?? ? ???
    _ = (base_url, token, resource, limit)
    return []
