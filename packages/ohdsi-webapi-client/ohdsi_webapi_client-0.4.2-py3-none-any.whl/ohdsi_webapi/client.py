from __future__ import annotations

from .auth import AuthStrategy
from .cache import cache_stats, clear_cache
from .http import HttpExecutor
from .models.cohort import CohortSubject
from .services.cohort_definition import CohortDefinitionService
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
        self.cohortdefs = CohortDefinitionService(self._http)
        self.jobs = JobsService(self._http)

        # Concept set methods
        self.conceptset_expression = self.concept_sets.expression
        self.conceptset_items = self.concept_sets.resolve
        self.conceptset_export = self.concept_sets.export
        self.conceptset_create = self.concept_sets.create
        self.conceptset_update = self.concept_sets.update
        self.conceptset_generationinfo = self.concept_sets.generation_info

        self.info = self.info_service.get

        # Cohort definition methods
        self.cohortdefinition_generate = self.cohortdefs.generate
        self.cohortdefinition_info = self.cohortdefs.generation_status
        self.cohortdefinition_inclusionrules = self.cohortdefs.inclusion_rules
        self.cohortdefinition_create = self.cohortdefs.create
        self.cohortdefinition_update = self.cohortdefs.update
        self.cohortdefinition_delete = self.cohortdefs.delete

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

    def cohort(self, id: int) -> list[CohortSubject]:
        """Get actual cohort patient data by cohort definition ID.

        Retrieves all cohort entities for the given cohort definition id from the COHORT table
        Returns the list of subjects/patients in the generated cohort.

        Equates to the WebAPI endpoint:
        GET /cohort/{id}
        """
        from .models.cohort import CohortSubject

        data = self._http.get(f"/cohort/{id}")
        return [CohortSubject.model_validate(item) for item in data]

    def cohortdefinition(self, id: int):
        """Get a specific cohort definition by ID.

        Equates to the WebAPI endpoints:

        GET /cohortdefinition
        GET /cohortdefinition/{id}
        """
        if id:
            return self.cohortdefs.get(id)
        else:
            return self.cohortdefs.list()

    def sources(self):
        """Get all available data sources.

        Returns
        -------
        list of Source
            List of available data source configurations.

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
