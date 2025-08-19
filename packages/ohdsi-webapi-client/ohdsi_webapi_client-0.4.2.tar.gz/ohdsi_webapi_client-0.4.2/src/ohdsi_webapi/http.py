from __future__ import annotations

import json
from typing import Any, Dict, Union

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .exceptions import WebApiError, raise_for_status

Json = Union[Dict[str, Any], list, str, int, float, bool, None]


class HttpExecutor:
    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 30.0,
        auth_headers_cb=None,
        user_agent: str = "ohdsi-webapi-client/0.1.0",
        verify: bool | str = True,
    ):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=timeout, headers={"User-Agent": user_agent}, verify=verify)
        self._auth_headers_cb = auth_headers_cb

    def close(self) -> None:
        self._client.close()

    def _headers(self, headers: dict[str, str] | None) -> dict[str, str]:
        merged = {}
        if self._auth_headers_cb:
            merged.update(self._auth_headers_cb())
        if headers:
            merged.update(headers)
        return merged

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, min=0.5, max=4), retry=retry_if_exception_type(httpx.HTTPError)
    )
    def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Json | None = None,
        headers: dict[str, str] | None = None,
    ) -> Json:
        url = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        try:
            resp = self._client.request(method.upper(), url, params=params, json=json_body, headers=self._headers(headers))
        except httpx.HTTPError as e:  # network issues
            raise WebApiError(str(e), endpoint=url) from e
        if resp.status_code >= 400:
            payload: Any
            try:
                payload = resp.json()
            except Exception:
                payload = resp.text
            message = payload.get("message") if isinstance(payload, dict) else str(payload)
            raise_for_status(resp.status_code, message or f"HTTP {resp.status_code}", endpoint=url, payload=payload)
        if resp.headers.get("Content-Type", "").startswith("application/json"):
            return resp.json()
        text = resp.text
        try:
            return json.loads(text)
        except Exception:
            return text

    def get(self, endpoint: str, **kwargs) -> Json:
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Json:
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Json:
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Json:
        return self.request("DELETE", endpoint, **kwargs)
