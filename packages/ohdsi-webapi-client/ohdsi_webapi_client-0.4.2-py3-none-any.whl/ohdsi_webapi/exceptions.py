from __future__ import annotations

from typing import Any


class WebApiError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, endpoint: str | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint
        self.payload = payload


class NotFoundError(WebApiError):
    pass


class UnauthorizedError(WebApiError):
    pass


class ForbiddenError(WebApiError):
    pass


class ConflictError(WebApiError):
    pass


class ServerError(WebApiError):
    pass


class ValidationError(WebApiError):
    pass


class JobTimeoutError(WebApiError):
    pass


HTTP_STATUS_MAP = {
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
}


def raise_for_status(status_code: int, message: str, *, endpoint: str, payload: Any) -> None:
    if 400 <= status_code < 500:
        exc_cls = HTTP_STATUS_MAP.get(status_code, WebApiError)
        raise exc_cls(message, status_code=status_code, endpoint=endpoint, payload=payload)
    if status_code >= 500:
        raise ServerError(message, status_code=status_code, endpoint=endpoint, payload=payload)
