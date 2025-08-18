from __future__ import annotations

from typing import Mapping


class AuthStrategy:
    def auth_headers(self) -> Mapping[str, str]:  # pragma: no cover - interface
        return {}


class BasicAuth(AuthStrategy):
    def __init__(self, username: str, password: str):
        import base64

        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        self._header = {"Authorization": f"Basic {token}"}

    def auth_headers(self):
        return self._header


class BearerToken(AuthStrategy):
    def __init__(self, token: str):
        self._token = token

    def auth_headers(self):
        return {"Authorization": f"Bearer {self._token}"}
