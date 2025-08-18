from __future__ import annotations


class RestSignClient:
    """Stub e-sign REST ?????"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def create_envelope(self, subject: str, recipients: list[str], doc: bytes | None = None) -> str:
        _ = (subject, recipients, doc)
        return "DUMMY_ENVELOPE_ID"

    def status(self, envelope_id: str) -> str:
        _ = envelope_id
        return "stub:unknown"
