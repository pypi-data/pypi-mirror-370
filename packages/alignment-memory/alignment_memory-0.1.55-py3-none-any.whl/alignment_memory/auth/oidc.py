from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class OIDCConfig:
    issuer: str | None = None
    client_id: str | None = None
    redirect_uri: str | None = None
    scopes: Sequence[str] = ("openid", "profile", "email")


def login(cfg: OIDCConfig) -> str:
    # Stub: ?? OIDC ?? ?? ?? ??
    return "DUMMY_OIDC_TOKEN"
