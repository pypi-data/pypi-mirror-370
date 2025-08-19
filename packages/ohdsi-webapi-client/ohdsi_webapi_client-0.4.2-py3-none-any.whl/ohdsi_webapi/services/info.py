from __future__ import annotations

from ..http import HttpExecutor
from ..models.info import WebApiInfo


class InfoService:
    """Service for retrieving WebAPI server information and metadata.

    This service provides access to basic WebAPI server information such as
    version numbers, build information, and server capabilities.
    """

    def __init__(self, http: HttpExecutor):
        self._http = http

    def get(self) -> WebApiInfo:
        """Get complete WebAPI server information.

        Returns
        -------
        WebApiInfo
            Object containing server version, build info, and other metadata.

        Examples
        --------
        >>> client = WebApiClient(base_url="http://localhost:8080/WebAPI")
        >>> info = client.info.get()
        >>> print(f"WebAPI Version: {info.version}")
        """
        data = self._http.get("/info")
        if isinstance(data, dict):
            return WebApiInfo(**data)
        return WebApiInfo()

    def version(self) -> str | None:
        """Get just the WebAPI version string.

        Returns
        -------
        str or None
            The WebAPI version string, or None if not available.

        Examples
        --------
        >>> client = WebApiClient(base_url="http://localhost:8080/WebAPI")
        >>> version = client.info.version()
        >>> print(f"Running WebAPI {version}")
        """
        return self.get().version
