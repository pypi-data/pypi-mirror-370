from __future__ import annotations

from .auth import AuthStrategy
from .cache import cache_stats, clear_cache
from .http import HttpExecutor
from .services.cohorts import CohortService
from .services.concept_sets import ConceptSetService
from .services.info import InfoService
from .services.jobs import JobsService
from .services.source import SourceService
from .services.vocabulary import VocabularyService


class WebApiClient:
    def __init__(self, base_url: str, *, auth: AuthStrategy | None = None, timeout: float = 30.0, verify: bool | str = True):
        self._http = HttpExecutor(
            base_url.rstrip("/"), timeout=timeout, auth_headers_cb=(auth.auth_headers if auth else None), verify=verify
        )

        # Core service objects (primary interface)
        self.info_service = InfoService(self._http)
        self.source = SourceService(self._http)
        self.vocabulary = VocabularyService(self._http)
        self.vocab = self.vocabulary  # Alias for convenience
        self.concept_sets = ConceptSetService(self._http)
        self.cohorts = CohortService(self._http)
        self.jobs = JobsService(self._http)

        # Explicit REST-style convenience methods
        # Concept set methods
        self.conceptset_expression = self.concept_sets.expression
        self.conceptset_items = self.concept_sets.resolve
        self.conceptset_export = self.concept_sets.export
        self.conceptset_create = self.concept_sets.create
        self.conceptset_update = self.concept_sets.update
        self.conceptset_generationinfo = self.concept_sets.generation_info

        self.info = self.info_service.get

        # Cohort
        self.cohort_update = self.cohorts.update
        self.cohort_create = self.cohorts.create
        self.cohort_delete = self.cohorts.delete

        # Cohort definition methods
        self.cohortdefinition_generate = self.cohorts.generate
        self.cohortdefinition_info = self.cohorts.generation_status
        self.cohortdefinition_inclusionrules = self.cohorts.inclusion_rules

        # Job methods
        self.job_status = self.jobs.status

    def conceptset(self, id: int | None = None):
        """Get all concept sets or a specific one by ID.

        Equates to the WebAPI endpoints:

        GET /conceptset
        GET /conceptset/{id}
        """
        if id:
            return self.concept_sets.get(id)
        else:
            return self.concept_sets.list()

    def cohort(self, id: int):
        """Get a specific cohort by ID.

        Equates to the WebAPI endpoint:

        GET /cohort/{id}
        """
        return self.cohorts.get(id)

    def sources(self):
        """Get all available data sources.

        .. deprecated::
            Use :attr:`source.sources()` instead. This method is kept for backward compatibility.

        Returns
        -------
        list of Source
            List of available data source configurations.

        Examples
        --------
        >>> # Old way (deprecated but still works)
        >>> sources = client.sources()
        >>>
        >>> # New preferred way
        >>> sources = client.source.sources()
        """
        return self.source.sources()

    def close(self):
        self._http.close()

    def __enter__(self):  # pragma: no cover
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover
        self.close()

    # Cache management methods
    def clear_cache(self) -> None:
        """Clear all cached data."""
        clear_cache()

    def cache_stats(self) -> dict:
        """Get cache statistics."""
        return cache_stats()
