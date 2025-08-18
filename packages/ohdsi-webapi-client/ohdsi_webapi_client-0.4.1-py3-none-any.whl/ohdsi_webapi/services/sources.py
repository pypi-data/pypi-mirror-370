from __future__ import annotations

from typing import Iterable

from ..http import HttpExecutor
from ..models.source import Source


class SourceService:
    """Service for managing OHDSI data sources.

    This service provides access to available data sources (CDM databases)
    configured in the WebAPI instance. Data sources are used for cohort
    generation, analysis, and vocabulary operations.
    """

    def __init__(self, http: HttpExecutor):
        self._http = http

    def sources(self) -> list[Source]:
        """List all available data sources.

        Returns
        -------
        list of Source
            List of available data source configurations, each containing
            source key, name, dialect, and connection information.

        Examples
        --------
        >>> client = WebApiClient(base_url="http://localhost:8080/WebAPI")
        >>> sources = client.source.sources()
        >>> for source in sources:
        ...     print(f"{source.source_name} ({source.source_key})")
        """
        data = self._http.get("/source/sources")
        if isinstance(data, list):
            return [Source(**d) for d in data if isinstance(d, dict)]
        return []

    def list(self) -> list[Source]:
        """List all available data sources.

        .. deprecated::
            Use :meth:`sources` instead. This method is kept for backward compatibility.

        Returns
        -------
        list of Source
            List of available data source configurations.
        """
        return self.sources()

    def iter(self) -> Iterable[Source]:
        """Iterate over all available data sources.

        Yields
        ------
        Source
            Each available data source configuration.

        Examples
        --------
        >>> client = WebApiClient(base_url="http://localhost:8080/WebAPI")
        >>> for source in client.source.iter():
        ...     print(f"Processing {source.source_name}")
        """
        yield from self.sources()
