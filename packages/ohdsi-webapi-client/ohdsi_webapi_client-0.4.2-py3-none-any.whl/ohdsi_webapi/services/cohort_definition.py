from __future__ import annotations

from typing import Any

from ..http import HttpExecutor
from ..models.cohort import CohortCount, CohortDefinition, InclusionRuleStats, JobStatus

# Import unified models for type hints and conversion
try:
    # Note: These imports may be used in future unified model support
    UNIFIED_MODELS_AVAILABLE = True
except ImportError:
    UNIFIED_MODELS_AVAILABLE = False

_TERMINAL_STATUSES = {"COMPLETED", "FAILED", "STOPPED"}


def _to_dict(obj: Any) -> dict[str, Any]:
    """Convert unified model to dict if needed, otherwise return as-is."""
    if hasattr(obj, "model_dump"):  # It's a Pydantic model
        return obj.model_dump(by_alias=True)
    elif hasattr(obj, "dict"):  # Older Pydantic version
        return obj.dict(by_alias=True)
    else:
        return obj  # Already a dict


def _is_unified_model(obj: Any) -> bool:
    """Check if object is a unified model (has Pydantic methods)."""
    return hasattr(obj, "model_dump") or hasattr(obj, "dict")


class CohortDefinitionService:
    """Service for managing cohort definitions and generation.

    This service provides comprehensive functionality for creating, managing,
    and generating cohorts in OHDSI WebAPI. It includes both low-level WebAPI
    operations and high-level helper methods for common cohort building patterns.
    """

    def __init__(self, http: HttpExecutor):
        self._http = http

    def list(self) -> list[CohortDefinition]:
        """List all cohort definitions (metadata only).

        Returns
        -------
        list[CohortDefinition]
            All available cohort definitions with metadata.

        Examples
        --------
        >>> cohorts = client.cohortdefs.list()
        >>> print(f"Found {len(cohorts)} cohort definitions")
        >>> for cohort in cohorts[:5]:  # Show first 5
        ...     print(f"  {cohort.id}: {cohort.name}")
        """
        data = self._http.get("/cohortdefinition/")
        if isinstance(data, list):
            out: list[CohortDefinition] = []
            for d in data:
                if isinstance(d, dict):
                    out.append(CohortDefinition(**d))
            return out
        return []

    def get(self, cohort_id: int) -> CohortDefinition:
        """Retrieve a cohort definition by ID.

        Parameters
        ----------
        cohort_id : int
            The unique identifier of the cohort definition to retrieve.

        Returns
        -------
        CohortDefinition
            The complete cohort definition including expression and metadata.

        Raises
        ------
        ValueError
            If the response format is unexpected or cohort not found.

        Examples
        --------
        >>> client = WebApiClient(base_url="http://localhost:8080/WebAPI")
        >>> cohort = client.cohortdefs.get(123)
        >>> print(f"Cohort: {cohort.name}")
        """
        data = self._http.get(f"/cohortdefinition/{cohort_id}")
        if isinstance(data, dict):
            return CohortDefinition(**data)
        raise ValueError("Unexpected cohort response")

    def create(self, cohort: CohortDefinition) -> CohortDefinition:
        """Create a new cohort definition.

        Parameters
        ----------
        cohort : CohortDefinition
            The cohort definition to create. The ID field will be ignored
            and assigned by the server.

        Returns
        -------
        CohortDefinition
            The created cohort definition with server-assigned ID and metadata.

        Raises
        ------
        ValueError
            If the response format is unexpected or creation failed.

        Examples
        --------
        >>> from ohdsi_webapi.models.cohort import CohortDefinition
        >>> cohort_def = CohortDefinition(
        ...     name="Test Cohort",
        ...     expression={"primaryCriteria": {...}}
        ... )
        >>> created = client.cohortdefs.create(cohort_def)
        >>> print(f"Created cohort ID: {created.id}")
        """
        payload = cohort.model_dump(exclude_none=True)
        data = self._http.post("/cohortdefinition/", json_body=payload)
        if isinstance(data, dict):
            return CohortDefinition(**data)
        raise ValueError("Unexpected create cohort response")

    def update(self, cohort: CohortDefinition) -> CohortDefinition:
        """Update an existing cohort definition.

        Parameters
        ----------
        cohort : CohortDefinition
            The cohort definition to update. Must include a valid ID.

        Returns
        -------
        CohortDefinition
            The updated cohort definition with server metadata.

        Raises
        ------
        ValueError
            If cohort.id is None or response format is unexpected.

        Examples
        --------
        >>> cohort = client.cohortdefs.get(123)
        >>> cohort.name = "Updated Name"
        >>> updated = client.cohortdefs.update(cohort)
        """
        if cohort.id is None:
            raise ValueError("CohortDefinition id required for update")
        payload = cohort.model_dump(exclude_none=True)
        data = self._http.put(f"/cohortdefinition/{cohort.id}", json_body=payload)
        if isinstance(data, dict):
            return CohortDefinition(**data)
        raise ValueError("Unexpected update cohort response")

    def delete(self, cohort_id: int) -> None:
        """Delete a cohort definition.

        Parameters
        ----------
        cohort_id : int
            The ID of the cohort definition to delete.

        Examples
        --------
        >>> client.cohortdefs.delete(123)
        """
        self._http.delete(f"/cohortdefinition/{cohort_id}")

    def generate(self, cohort_id: int, source_key: str) -> JobStatus:
        """Start cohort generation on a specific data source.

        Parameters
        ----------
        cohort_id : int
            The ID of the cohort definition to generate.
        source_key : str
            The key of the data source to generate the cohort on.

        Returns
        -------
        JobStatus
            Initial job status with execution ID for tracking progress.

        Examples
        --------
        >>> status = client.cohortdefs.generate(cohort_id=123, source_key="SYNPUF1K")
        >>> print(f"Generation started: {status.execution_id}")
        """
        data = self._http.get(f"/cohortdefinition/{cohort_id}/generate/{source_key}")
        if isinstance(data, dict):
            return JobStatus(status=data.get("status", "UNKNOWN"), executionId=data.get("executionId"))
        return JobStatus(status="UNKNOWN")

    def generation_status(self, cohort_id: int, source_key: str) -> JobStatus:
        """Check the status of a cohort generation job.

        Parameters
        ----------
        cohort_id : int
            The ID of the cohort definition.
        source_key : str
            The key of the data source.

        Returns
        -------
        JobStatus
            Current job status and execution information.

        Examples
        --------
        >>> status = client.cohortdefs.generation_status(123, "SYNPUF1K")
        >>> print(f"Status: {status.status}")
        """
        data = self._http.get(f"/cohortdefinition/{cohort_id}/info")  # includes generation info
        if isinstance(data, dict):
            gen_list = data.get("generationInfo", [])
            for item in gen_list:
                if item.get("sourceKey") == source_key:
                    return JobStatus(status=item.get("status", "UNKNOWN"), executionId=item.get("executionId"))
        return JobStatus(status="UNKNOWN")

    def poll_generation(self, cohort_id: int, source_key: str, max_wait: int = 300) -> JobStatus:
        """Poll cohort generation until completion or timeout.

        This method will continuously check the generation status until the job
        completes (successfully or with failure) or the timeout is reached.

        Parameters
        ----------
        cohort_id : int
            The ID of the cohort definition being generated.
        source_key : str
            The key of the data source.
        max_wait : int, default 300
            Maximum time to wait in seconds before timing out.

        Returns
        -------
        JobStatus
            Final job status when completed or timed out.

        Examples
        --------
        >>> # Start generation and wait for completion
        >>> client.cohortdefs.generate(123, "SYNPUF1K")
        >>> final_status = client.cohortdefs.poll_generation(123, "SYNPUF1K")
        >>> if final_status.status == "COMPLETED":
        ...     print("Generation successful!")
        """
        import time

        start_time = time.time()
        while time.time() - start_time < max_wait:
            status = self.generation_status(cohort_id, source_key)
            if status.status in _TERMINAL_STATUSES:
                return status
            time.sleep(5)  # Wait 5 seconds before next check
        return JobStatus(status="TIMEOUT")

    def counts(self, cohort_id: int) -> list[CohortCount]:
        """Get cohort subject counts for all data sources.

        Parameters
        ----------
        cohort_id : int
            The ID of the cohort definition.

        Returns
        -------
        list of CohortCount
            Count information for each data source where the cohort was generated.

        Examples
        --------
        >>> counts = client.cohortdefs.counts(123)
        >>> for count in counts:
        ...     print(f"{count.source_key}: {count.subject_count:,} subjects")
        """
        data = self._http.get(f"/cohortdefinition/{cohort_id}/info")
        counts = []
        if isinstance(data, dict):
            gen_info = data.get("generationInfo", [])
            for item in gen_info:
                if item.get("status") == "COMPLETED":
                    counts.append(
                        CohortCount(
                            sourceKey=item.get("sourceKey", ""),
                            subjectCount=item.get("personCount", 0),
                            recordCount=item.get("recordCount", 0),
                        )
                    )
        return counts

    def inclusion_rules(self, cohort_id: int, source_key: str) -> list[InclusionRuleStats]:
        # After generation, inclusion stats: /cohortdefinition/{id}/inclusionrules/{sourceKey}
        data = self._http.get(f"/cohortdefinition/{cohort_id}/inclusionrules/{source_key}")
        if isinstance(data, list):
            return [InclusionRuleStats(**d) for d in data if isinstance(d, dict)]
        return []

    # Cohort Building Helpers

    def create_concept_set(self, concept_id: int | Any, name: str, include_descendants: bool = True) -> dict[str, Any]:
        """Create a concept set for use in cohort definitions.

        A concept set defines a collection of OMOP concepts that represent a clinical
        entity (like "Type 2 Diabetes" or "Hypertension"). This is a fundamental
        building block for cohort definitions.

        Parameters
        ----------
        concept_id : int or Concept
            The OMOP concept ID (e.g., 201826 for Type 2 diabetes mellitus) OR
            a unified Concept model object. If a Concept object is provided,
            the concept_id, name, and other attributes will be extracted from it.
        name : str
            Human-readable name for the concept set (e.g., "Type 2 Diabetes").
            Ignored if concept_id is a Concept object (name taken from Concept).
        include_descendants : bool, default True
            Whether to include descendant concepts in the hierarchy.
            True means more inclusive matching (recommended for most cases).

        Returns
        -------
        dict
            A concept set definition that can be used in cohort expressions.
            Contains 'id', 'name', and 'expression' fields.

        Examples
        --------
        >>> # Traditional usage with concept ID
        >>> diabetes_cs = client.cohortdefs.create_concept_set(
        ...     concept_id=201826,
        ...     name="Type 2 Diabetes",
        ...     include_descendants=True
        ... )
        >>>
        >>> # NEW: Using unified Concept model
        >>> from ohdsi_cohort_schemas import Concept
        >>> concept = Concept(
        ...     concept_id=201826,
        ...     concept_name="Type 2 diabetes mellitus",
        ...     vocabulary_id="SNOMED"
        ... )
        >>> diabetes_cs = client.cohortdefs.create_concept_set(
        ...     concept_id=concept,  # Pass Concept object directly
        ...     name="",  # Ignored - taken from Concept
        ...     include_descendants=True
        ... )
        >>>
        >>> # Use in cohort expression (both ways produce same result)
        >>> expression = client.cohortdefs.create_base_cohort_expression([diabetes_cs])

        Notes
        -----
        The include_descendants parameter is important for clinical concepts:
        - True: Includes all child concepts (e.g., "Type 2 diabetes with complications")
        - False: Exact concept match only (more restrictive)

        When passing a Concept object, the name parameter is ignored and the
        concept_name from the Concept object is used instead.
        """
        # Handle both int concept_id and Concept object
        if _is_unified_model(concept_id):
            # It's a unified Concept model
            concept_dict = _to_dict(concept_id)
            actual_concept_id = concept_dict.get("concept_id") or concept_dict.get("CONCEPT_ID")
            actual_name = concept_dict.get("concept_name") or concept_dict.get("CONCEPT_NAME") or name
        else:
            # It's a traditional int concept_id
            actual_concept_id = concept_id
            actual_name = name

        return {
            "id": 0,  # Will be assigned when used in expression
            "name": actual_name,
            "expression": {
                "items": [
                    {
                        "concept": {
                            "conceptId": actual_concept_id,
                            "includeDescendants": include_descendants,
                            "includeMapped": False,
                            "isExcluded": False,
                        }
                    }
                ]
            },
        }

    def create_base_cohort_expression(self, concept_sets: list[dict[str, Any] | Any], primary_concept_set_id: int = 0) -> dict[str, Any]:
        """Create a basic cohort expression with just primary criteria.

        This creates the foundation for a cohort definition by establishing the
        primary inclusion criteria. Additional filters (age, gender, etc.) can
        be added using the add_*_filter methods.

        Parameters
        ----------
        concept_sets : list of dict or list of ConceptSetExpression
            List of concept set definitions created with create_concept_set() OR
            a list of unified ConceptSetExpression model objects.
            Each concept set represents a clinical entity for inclusion.
        primary_concept_set_id : int, default 0
            Index of the concept set to use as primary criteria (0-based).

        Returns
        -------
        dict
            A complete cohort expression with primary criteria defined.
            This can be used directly in a CohortDefinition or extended with filters.

        Examples
        --------
        >>> # Traditional usage with dicts
        >>> diabetes_cs = client.cohortdefs.create_concept_set(201826, "Diabetes")
        >>> hypertension_cs = client.cohortdefs.create_concept_set(316866, "Hypertension")
        >>> expression = client.cohortdefs.create_base_cohort_expression(
        ...     concept_sets=[diabetes_cs, hypertension_cs],
        ...     primary_concept_set_id=0  # Use diabetes as primary
        ... )
        >>>
        >>> # NEW: Using unified models
        >>> from ohdsi_cohort_schemas import ConceptSetExpression
        >>> diabetes_expr = ConceptSetExpression(items=[...])  # Unified model
        >>> expression = client.cohortdefs.create_base_cohort_expression(
        ...     concept_sets=[diabetes_expr],  # Pass unified models directly
        ...     primary_concept_set_id=0
        ... )
        >>>
        >>> # Use in cohort definition (both ways work)
        >>> cohort = CohortDefinition(
        ...     name="Diabetes Patients",
        ...     expression=expression
        ... )
        """
        # Convert unified models to dicts if needed
        concept_sets_dicts = []
        for cs in concept_sets:
            if _is_unified_model(cs):
                # It's a ConceptSetExpression or similar unified model
                cs_dict = _to_dict(cs)
                # Ensure it has the expected structure for legacy methods
                if "items" in cs_dict and "id" not in cs_dict:
                    # Convert ConceptSetExpression to legacy format
                    cs_dict = {
                        "id": 0,  # Will be reassigned below
                        "name": cs_dict.get("name", f"Concept Set {len(concept_sets_dicts)}"),
                        "expression": cs_dict,  # The ConceptSetExpression becomes the expression
                    }
                concept_sets_dicts.append(cs_dict)
            else:
                # Already a dict - use as-is
                concept_sets_dicts.append(cs)

        # Assign IDs to concept sets
        for i, cs in enumerate(concept_sets_dicts):
            cs["id"] = i

        # Create primary criteria using the specified concept set
        primary_criteria = {
            "criteriaList": [{"conditionOccurrence": {"conceptSetId": primary_concept_set_id}}],
            "observationWindow": {"priorDays": 0, "postDays": 0},
            "primaryCriteriaLimit": {"type": "First"},
        }

        return {
            "conceptSets": concept_sets_dicts,
            "primaryCriteria": primary_criteria,
            "additionalCriteria": {"type": "ALL", "criteriaList": [], "demographicCriteriaList": [], "groups": []},
            "qualifiedLimit": {"type": "First"},
            "expressionLimit": {"type": "First"},
            "inclusionRules": [],
            "endStrategy": {"type": "DEFAULT"},
            "censorWindow": {},
        }

    def add_gender_filter(self, expression: dict[str, Any] | Any, gender: str = "male") -> dict[str, Any]:
        """Add gender filter to an existing cohort expression.

        This method adds an inclusion rule that restricts the cohort to subjects
        of a specific gender. The filter is applied as an additional inclusion
        criterion that must be met during the index date window.

        Parameters
        ----------
        expression : dict or CohortExpression
            An existing cohort expression to modify (from create_base_cohort_expression)
            OR a unified CohortExpression model object.
        gender : str, default "male"
            Gender to filter for. Valid values: "male", "female".

        Returns
        -------
        dict
            Modified cohort expression with gender filter applied as an inclusion rule.

        Examples
        --------
        >>> # Traditional usage with dict
        >>> diabetes_cs = client.cohortdefs.create_concept_set(201826, "Diabetes")
        >>> expression = client.cohortdefs.create_base_cohort_expression([diabetes_cs])
        >>> male_expression = client.cohortdefs.add_gender_filter(expression, "male")
        >>>
        >>> # NEW: Using unified models
        >>> from ohdsi_cohort_schemas import CohortExpression
        >>> expr_model = CohortExpression(...)  # Unified model
        >>> male_expression = client.cohortdefs.add_gender_filter(expr_model, "male")
        >>>
        >>> # Create cohort (both ways work)
        >>> cohort = CohortDefinition(
        ...     name="Male Diabetes Patients",
        ...     expression=male_expression
        ... )

        Notes
        -----
        Gender codes in OMOP:
        - "male": OMOP concept ID 8507
        - "female": OMOP concept ID 8532

        The filter is implemented as an inclusion rule that requires the subject
        to have the specified gender during the index date window.
        """
        # Convert unified model to dict if needed
        expression_dict = _to_dict(expression)

        gender_concept_id = 8507 if gender.lower() == "male" else 8532
        gender_rule = {
            "name": f"{gender.title()} gender",
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {"person": {"genderConcept": [{"conceptId": gender_concept_id, "conceptName": gender.upper()}]}},
                        "startWindow": {"start": {"coeff": -1}, "end": {"coeff": 1}, "useIndexEnd": False, "useEventEnd": False},
                        "occurrence": {"type": 2, "count": 1},
                    }
                ],
            },
        }

        new_expression = expression_dict.copy()
        new_expression["inclusionRules"] = [*expression_dict.get("inclusionRules", []), gender_rule]
        return new_expression

    def add_age_filter(self, expression: dict[str, Any], min_age: int, max_age: int | None = None) -> dict[str, Any]:
        """Add age filter to an existing cohort expression.

        This method adds an inclusion rule that restricts the cohort to subjects
        within a specific age range at the index date. Age is calculated as the
        difference between the index date and the person's birth year.

        Parameters
        ----------
        expression : dict
            An existing cohort expression to modify.
        min_age : int
            Minimum age at index date (inclusive).
        max_age : int, optional
            Maximum age at index date (inclusive). If None, no upper age limit.

        Returns
        -------
        dict
            Modified cohort expression with age filter applied as an inclusion rule.

        Examples
        --------
        >>> # Add minimum age filter
        >>> expression = client.cohortdefs.add_age_filter(expression, min_age=18)
        >>>
        >>> # Add age range filter
        >>> expression = client.cohortdefs.add_age_filter(
        ...     expression,
        ...     min_age=40,
        ...     max_age=65
        ... )

        Notes
        -----
        Age calculations in OMOP use the year of birth from the PERSON table.
        The age filter is applied at the index date (when the primary criteria
        event occurs).
        """
        age_criteria = {"ageAtStart": {"value": min_age, "op": "gte"}}
        rule_name = f"Age >= {min_age}"

        if max_age is not None:
            # For age range, need both min and max criteria
            age_criteria = [{"ageAtStart": {"value": min_age, "op": "gte"}}, {"ageAtStart": {"value": max_age, "op": "lte"}}]
            rule_name = f"Age {min_age}-{max_age}"

        age_rule = {
            "name": rule_name,
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {"person": age_criteria if isinstance(age_criteria, list) else age_criteria},
                        "startWindow": {"start": {"coeff": -1}, "end": {"coeff": 1}, "useIndexEnd": False, "useEventEnd": False},
                        "occurrence": {"type": 2, "count": 1},
                    }
                ],
            },
        }

        new_expression = expression.copy()
        new_expression["inclusionRules"] = [*expression.get("inclusionRules", []), age_rule]
        return new_expression

    def add_time_window_filter(
        self, expression: dict[str, Any], concept_set_id: int, days_before: int, days_after: int = 0, filter_name: str | None = None
    ) -> dict[str, Any]:
        """Add time-window based condition filter.

        Args:
            expression: Existing cohort expression
            concept_set_id: Which concept set to look for
            days_before: How many days before index date to look (positive number)
            days_after: How many days after index date to look
            filter_name: Name for this filter rule

        Returns:
            Updated cohort expression with time window inclusion rule
        """
        if not filter_name:
            filter_name = f"Condition in last {days_before} days"

        time_rule = {
            "name": filter_name,
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {"conditionOccurrence": {"conceptSetId": concept_set_id}},
                        "startWindow": {
                            "start": {"coeff": -days_before},
                            "end": {"coeff": days_after},
                            "useIndexEnd": False,
                            "useEventEnd": False,
                        },
                        "occurrence": {"type": 2, "count": 1},
                    }
                ],
            },
        }

        new_expression = expression.copy()
        new_expression["inclusionRules"] = [*expression.get("inclusionRules", []), time_rule]
        return new_expression

    def add_observation_period_filter(self, expression: dict[str, Any], days_before: int = 365, days_after: int = 0) -> dict[str, Any]:
        """Add observation period requirement (continuous enrollment).

        Args:
            expression: Existing cohort expression
            days_before: Required observation days before index date
            days_after: Required observation days after index date

        Returns:
            Updated cohort expression with observation period requirement
        """
        obs_rule = {
            "name": f"Continuous observation {days_before} days before, {days_after} days after",
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {
                            "observationPeriod": {
                                "periodStartDate": {"value": days_before, "op": "gte"},
                                "periodEndDate": {"value": days_after, "op": "gte"},
                            }
                        },
                        "startWindow": {
                            "start": {"coeff": -days_before},
                            "end": {"coeff": days_after},
                            "useIndexEnd": False,
                            "useEventEnd": False,
                        },
                        "occurrence": {"type": 2, "count": 1},
                    }
                ],
            },
        }

        new_expression = expression.copy()
        new_expression["inclusionRules"] = [*expression.get("inclusionRules", []), obs_rule]
        return new_expression

    def add_visit_filter(
        self,
        expression: dict[str, Any],
        visit_concept_ids: list[int],
        days_before: int = 30,
        days_after: int = 0,
        filter_name: str | None = None,
    ) -> dict[str, Any]:
        """Add visit occurrence filter (inpatient, outpatient, ER, etc.).

        Args:
            expression: Existing cohort expression
            visit_concept_ids: List of visit concept IDs (9201=Inpatient, 9202=Outpatient, 9203=ER)
            days_before: Days before index to look for visit
            days_after: Days after index to look for visit
            filter_name: Name for this filter

        Returns:
            Updated cohort expression with visit filter
        """
        if not filter_name:
            visit_types = {9201: "Inpatient", 9202: "Outpatient", 9203: "Emergency", 9204: "Long-term care"}
            names = [visit_types.get(vid, f"Visit {vid}") for vid in visit_concept_ids]
            filter_name = f"Had {'/'.join(names)} visit"

        visit_rule = {
            "name": filter_name,
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {"visitOccurrence": {"visitType": [{"conceptId": vid} for vid in visit_concept_ids]}},
                        "startWindow": {
                            "start": {"coeff": -days_before},
                            "end": {"coeff": days_after},
                            "useIndexEnd": False,
                            "useEventEnd": False,
                        },
                        "occurrence": {"type": 2, "count": 1},
                    }
                ],
            },
        }

        new_expression = expression.copy()
        new_expression["inclusionRules"] = [*expression.get("inclusionRules", []), visit_rule]
        return new_expression

    def add_measurement_filter(
        self,
        expression: dict[str, Any],
        concept_set_id: int,
        value_min: float | None = None,
        value_max: float | None = None,
        unit_concept_id: int | None = None,
        days_before: int = 365,
        days_after: int = 0,
        filter_name: str | None = None,
    ) -> dict[str, Any]:
        """Add measurement filter (lab values, vital signs, etc.).

        Args:
            expression: Existing cohort expression
            concept_set_id: Measurement concept set ID
            value_min: Minimum measurement value
            value_max: Maximum measurement value
            unit_concept_id: Required unit concept ID
            days_before: Days before index to look for measurement
            days_after: Days after index to look for measurement
            filter_name: Name for this filter

        Returns:
            Updated cohort expression with measurement filter
        """
        if not filter_name:
            filter_name = "Measurement in range"
            if value_min is not None and value_max is not None:
                filter_name = f"Measurement {value_min}-{value_max}"
            elif value_min is not None:
                filter_name = f"Measurement >= {value_min}"
            elif value_max is not None:
                filter_name = f"Measurement <= {value_max}"

        measurement_criteria = {"conceptSetId": concept_set_id}

        # Add value constraints if specified
        if value_min is not None or value_max is not None:
            measurement_criteria["valueAsNumber"] = {}
            if value_min is not None:
                measurement_criteria["valueAsNumber"]["value"] = value_min
                measurement_criteria["valueAsNumber"]["op"] = "gte"
            if value_max is not None:
                # For range, need to handle differently
                if value_min is not None:
                    measurement_criteria["valueAsNumber"] = [{"value": value_min, "op": "gte"}, {"value": value_max, "op": "lte"}]
                else:
                    measurement_criteria["valueAsNumber"]["value"] = value_max
                    measurement_criteria["valueAsNumber"]["op"] = "lte"

        if unit_concept_id is not None:
            measurement_criteria["unit"] = [{"conceptId": unit_concept_id}]

        measurement_rule = {
            "name": filter_name,
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {"measurement": measurement_criteria},
                        "startWindow": {
                            "start": {"coeff": -days_before},
                            "end": {"coeff": days_after},
                            "useIndexEnd": False,
                            "useEventEnd": False,
                        },
                        "occurrence": {"type": 2, "count": 1},
                    }
                ],
            },
        }

        new_expression = expression.copy()
        new_expression["inclusionRules"] = [*expression.get("inclusionRules", []), measurement_rule]
        return new_expression

    def add_drug_era_filter(
        self,
        expression: dict[str, Any],
        concept_set_id: int,
        era_length_min: int | None = None,
        era_length_max: int | None = None,
        days_before: int = 365,
        days_after: int = 0,
        filter_name: str | None = None,
    ) -> dict[str, Any]:
        """Add drug era filter (continuous medication exposure).

        Args:
            expression: Existing cohort expression
            concept_set_id: Drug concept set ID
            era_length_min: Minimum era length in days
            era_length_max: Maximum era length in days
            days_before: Days before index to look for drug era
            days_after: Days after index to look for drug era
            filter_name: Name for this filter

        Returns:
            Updated cohort expression with drug era filter
        """
        if not filter_name:
            filter_name = "Drug era"
            if era_length_min is not None:
                filter_name = f"Drug era >= {era_length_min} days"

        drug_era_criteria = {"conceptSetId": concept_set_id}

        if era_length_min is not None or era_length_max is not None:
            drug_era_criteria["eraLength"] = {}
            if era_length_min is not None:
                drug_era_criteria["eraLength"]["value"] = era_length_min
                drug_era_criteria["eraLength"]["op"] = "gte"
            if era_length_max is not None:
                if era_length_min is not None:
                    drug_era_criteria["eraLength"] = [{"value": era_length_min, "op": "gte"}, {"value": era_length_max, "op": "lte"}]
                else:
                    drug_era_criteria["eraLength"]["value"] = era_length_max
                    drug_era_criteria["eraLength"]["op"] = "lte"

        drug_era_rule = {
            "name": filter_name,
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {"drugEra": drug_era_criteria},
                        "startWindow": {
                            "start": {"coeff": -days_before},
                            "end": {"coeff": days_after},
                            "useIndexEnd": False,
                            "useEventEnd": False,
                        },
                        "occurrence": {"type": 2, "count": 1},
                    }
                ],
            },
        }

        new_expression = expression.copy()
        new_expression["inclusionRules"] = [*expression.get("inclusionRules", []), drug_era_rule]
        return new_expression

    def add_prior_observation_filter(self, expression: dict[str, Any], min_days: int = 365) -> dict[str, Any]:
        """Add prior observation requirement (data quality filter).

        Args:
            expression: Existing cohort expression
            min_days: Minimum days of prior observation required

        Returns:
            Updated cohort expression with prior observation requirement
        """
        prior_obs_rule = {
            "name": f"At least {min_days} days prior observation",
            "expression": {
                "type": "ALL",
                "criteriaList": [
                    {
                        "criteria": {"person": {"priorEnrollDays": {"value": min_days, "op": "gte"}}},
                        "startWindow": {"start": {"coeff": -1}, "end": {"coeff": 1}, "useIndexEnd": False, "useEventEnd": False},
                        "occurrence": {"type": 2, "count": 1},
                    }
                ],
            },
        }

        new_expression = expression.copy()
        new_expression["inclusionRules"] = [*expression.get("inclusionRules", []), prior_obs_rule]
        return new_expression

    def add_multiple_conditions_filter(
        self,
        expression: dict[str, Any],
        concept_set_ids: list[int],
        logic: str = "ALL",
        days_before: int = 365,
        days_after: int = 0,
        filter_name: str | None = None,
    ) -> dict[str, Any]:
        """Add filter requiring multiple conditions.

        Args:
            expression: Existing cohort expression
            concept_set_ids: List of concept set IDs for conditions
            logic: "ALL" (must have all conditions) or "ANY" (must have at least one)
            days_before: Days before index to look for conditions
            days_after: Days after index to look for conditions
            filter_name: Name for this filter

        Returns:
            Updated cohort expression with multiple conditions filter
        """
        if not filter_name:
            filter_name = f"Has {logic.lower()} of {len(concept_set_ids)} conditions"

        criteria_list = []
        for cs_id in concept_set_ids:
            criteria_list.append(
                {
                    "criteria": {"conditionOccurrence": {"conceptSetId": cs_id}},
                    "startWindow": {
                        "start": {"coeff": -days_before},
                        "end": {"coeff": days_after},
                        "useIndexEnd": False,
                        "useEventEnd": False,
                    },
                    "occurrence": {"type": 2, "count": 1},
                }
            )

        multiple_conditions_rule = {"name": filter_name, "expression": {"type": logic, "criteriaList": criteria_list}}  # "ALL" or "ANY"

        new_expression = expression.copy()
        new_expression["inclusionRules"] = [*expression.get("inclusionRules", []), multiple_conditions_rule]
        return new_expression

    # Exclusion Criteria Methods

    def add_exclusion_condition(
        self,
        expression: dict[str, Any],
        concept_set_id: int,
        days_before: int = 365,
        days_after: int = 0,
        exclusion_name: str | None = None,
    ) -> dict[str, Any]:
        """Add exclusion criteria to prevent people with certain conditions from entering cohort.

        Args:
            expression: Existing cohort expression
            concept_set_id: Which concept set represents the exclusion condition
            days_before: How many days before index date to look for exclusion
            days_after: How many days after index date to look for exclusion
            exclusion_name: Name for this exclusion rule

        Returns:
            Updated cohort expression with exclusion criteria
        """
        if not exclusion_name:
            exclusion_name = f"Exclude if condition in {days_before} days before index"

        exclusion_rule = {
            "type": "ALL",
            "criteriaList": [
                {
                    "criteria": {"conditionOccurrence": {"conceptSetId": concept_set_id}},
                    "startWindow": {
                        "start": {"coeff": -days_before},
                        "end": {"coeff": days_after},
                        "useIndexEnd": False,
                        "useEventEnd": False,
                    },
                    "occurrence": {"type": 0, "count": 0},  # 0 = exactly 0 occurrences (exclusion)
                }
            ],
        }

        new_expression = expression.copy()
        current_exclusions = expression.get("exclusionCriteria", [])
        new_expression["exclusionCriteria"] = [*current_exclusions, exclusion_rule]
        return new_expression

    def add_exclusion_drug(
        self,
        expression: dict[str, Any],
        concept_set_id: int,
        days_before: int = 365,
        days_after: int = 0,
        exclusion_name: str | None = None,
    ) -> dict[str, Any]:
        """Add drug exclusion criteria (e.g., exclude if taking certain medication).

        Args:
            expression: Existing cohort expression
            concept_set_id: Which concept set represents the exclusion drug
            days_before: How many days before index date to look for drug exposure
            days_after: How many days after index date to look for drug exposure
            exclusion_name: Name for this exclusion rule

        Returns:
            Updated cohort expression with drug exclusion criteria
        """
        if not exclusion_name:
            exclusion_name = f"Exclude if drug exposure in {days_before} days before index"

        exclusion_rule = {
            "type": "ALL",
            "criteriaList": [
                {
                    "criteria": {"drugExposure": {"conceptSetId": concept_set_id}},
                    "startWindow": {
                        "start": {"coeff": -days_before},
                        "end": {"coeff": days_after},
                        "useIndexEnd": False,
                        "useEventEnd": False,
                    },
                    "occurrence": {"type": 0, "count": 0},  # 0 = exactly 0 occurrences (exclusion)
                }
            ],
        }

        new_expression = expression.copy()
        current_exclusions = expression.get("exclusionCriteria", [])
        new_expression["exclusionCriteria"] = [*current_exclusions, exclusion_rule]
        return new_expression

    def add_exclusion_procedure(
        self,
        expression: dict[str, Any],
        concept_set_id: int,
        days_before: int = 365,
        days_after: int = 0,
        exclusion_name: str | None = None,
    ) -> dict[str, Any]:
        """Add procedure exclusion criteria (e.g., exclude if had certain surgery).

        Args:
            expression: Existing cohort expression
            concept_set_id: Which concept set represents the exclusion procedure
            days_before: How many days before index date to look for procedure
            days_after: How many days after index date to look for procedure
            exclusion_name: Name for this exclusion rule

        Returns:
            Updated cohort expression with procedure exclusion criteria
        """
        if not exclusion_name:
            exclusion_name = f"Exclude if procedure in {days_before} days before index"

        exclusion_rule = {
            "type": "ALL",
            "criteriaList": [
                {
                    "criteria": {"procedureOccurrence": {"conceptSetId": concept_set_id}},
                    "startWindow": {
                        "start": {"coeff": -days_before},
                        "end": {"coeff": days_after},
                        "useIndexEnd": False,
                        "useEventEnd": False,
                    },
                    "occurrence": {"type": 0, "count": 0},  # 0 = exactly 0 occurrences (exclusion)
                }
            ],
        }

        new_expression = expression.copy()
        current_exclusions = expression.get("exclusionCriteria", [])
        new_expression["exclusionCriteria"] = [*current_exclusions, exclusion_rule]
        return new_expression

    def add_exclusion_death(self, expression: dict[str, Any], days_after_index: int = 30) -> dict[str, Any]:
        """Add death exclusion criteria (e.g., exclude if died within X days of index).

        Args:
            expression: Existing cohort expression
            days_after_index: Exclude if death occurs within this many days after index

        Returns:
            Updated cohort expression with death exclusion criteria
        """
        exclusion_rule = {
            "type": "ALL",
            "criteriaList": [
                {
                    "criteria": {"death": {}},  # Death criteria
                    "startWindow": {
                        "start": {"coeff": 0},  # Index date
                        "end": {"coeff": days_after_index},
                        "useIndexEnd": False,
                        "useEventEnd": False,
                    },
                    "occurrence": {"type": 0, "count": 0},  # 0 = exactly 0 occurrences (exclusion)
                }
            ],
        }

        new_expression = expression.copy()
        current_exclusions = expression.get("exclusionCriteria", [])
        new_expression["exclusionCriteria"] = [*current_exclusions, exclusion_rule]
        return new_expression

    async def build_incremental_cohort(
        self,
        source_key: str,
        base_name: str,
        concept_sets: list[dict[str, Any]],
        filters: list[dict[str, Any]],
        exclusions: list[dict[str, Any]] | None = None,
    ) -> list[tuple[CohortDefinition, int]]:
        """Build a cohort incrementally, applying filters and exclusions step by step.

        This is a high-level method that automates the process of building complex
        cohorts by applying inclusion filters and exclusion criteria one at a time.
        Each step creates a new cohort definition, generates it, and returns the
        subject count, allowing you to see the impact of each filter.

        Parameters
        ----------
        source_key : str
            The data source key to generate cohorts against (e.g., "SYNPUF1K").
        base_name : str
            Base name for the cohort series. Each step will append step information.
        concept_sets : list of dict
            List of concept set definitions created with create_concept_set().
        filters : list of dict
            List of inclusion filter definitions. Each dict should have a 'type' key
            and appropriate parameters for that filter type.
        exclusions : list of dict, optional
            List of exclusion criteria definitions to apply after inclusion filters.

        Returns
        -------
        list of tuple[CohortDefinition, int]
            List of (cohort_definition, subject_count) tuples for each step.
            Allows tracking how each filter affects the cohort size.

        Examples
        --------
        >>> # Define concept sets
        >>> diabetes_cs = client.cohortdefs.create_concept_set(201826, "Diabetes")
        >>>
        >>> # Define filters to apply incrementally
        >>> filters = [
        ...     {"type": "gender", "gender": "male"},
        ...     {"type": "age", "min_age": 40, "max_age": 75},
        ...     {"type": "observation_period", "min_days": 365}
        ... ]
        >>>
        >>> # Define exclusions
        >>> exclusions = [
        ...     {"type": "condition", "concept_set_id": 1, "days_before": 365,
        ...      "name": "No cancer history"},
        ...     {"type": "drug", "concept_set_id": 2, "days_before": 30,
        ...      "name": "No recent chemotherapy"}
        ... ]
        >>>
        >>> # Build incrementally
        >>> results = await client.cohortdefs.build_incremental_cohort(
        ...     source_key="SYNPUF1K",
        ...     base_name="Diabetes Study",
        ...     concept_sets=[diabetes_cs],
        ...     filters=filters,
        ...     exclusions=exclusions
        ... )
        >>>
        >>> # See the impact of each step
        >>> for i, (cohort, count) in enumerate(results):
        ...     print(f"Step {i+1}: {count:,} subjects - {cohort.name}")

        Notes
        -----
        Supported filter types:
        - "gender": requires 'gender' parameter ("male" or "female")
        - "age": requires 'min_age' and optionally 'max_age'
        - "observation_period": requires 'min_days' parameter
        - "visit": requires 'visit_concept_id' parameter
        - "measurement": requires 'measurement_concept_id' parameter

        Supported exclusion types:
        - "condition": requires 'concept_set_id', 'days_before', 'name'
        - "drug": requires 'concept_set_id', 'days_before', 'name'
        - "procedure": requires 'concept_set_id', 'days_before', 'name'
        - "death": requires 'days_before', 'name'

        This method is asynchronous because it creates, generates, and polls
        multiple cohorts sequentially, which can take significant time.
        """
        results = []

        # Step 1: Base cohort with primary criteria only
        expression = self.create_base_cohort_expression(concept_sets)
        cohort = CohortDefinition(name=f"{base_name} - Step 1: Base criteria", expression=expression)

        created_cohort = self.create(cohort)
        self.generate(created_cohort.id, source_key)
        self.poll_generation(created_cohort.id, source_key)
        counts = self.counts(created_cohort.id)
        subject_count = counts[0].subject_count if counts else 0
        results.append((created_cohort, subject_count))

        # Apply inclusion filters incrementally
        current_expression = expression
        step_num = 2

        for filter_def in filters:
            filter_type = filter_def.get("type")

            if filter_type == "gender":
                current_expression = self.add_gender_filter(current_expression, filter_def.get("gender", "male"))
            elif filter_type == "age":
                current_expression = self.add_age_filter(current_expression, filter_def.get("min_age"), filter_def.get("max_age"))
            elif filter_type == "time_window":
                current_expression = self.add_time_window_filter(
                    current_expression,
                    filter_def.get("concept_set_id", 0),
                    filter_def.get("days_before", 365),
                    filter_def.get("days_after", 0),
                    filter_def.get("filter_name"),
                )
            elif filter_type == "observation_period":
                current_expression = self.add_observation_period_filter(
                    current_expression, filter_def.get("days_before", 365), filter_def.get("days_after", 0)
                )
            elif filter_type == "visit":
                current_expression = self.add_visit_filter(
                    current_expression,
                    filter_def.get("visit_concept_ids", [9201]),  # Default to inpatient
                    filter_def.get("days_before", 30),
                    filter_def.get("days_after", 0),
                    filter_def.get("filter_name"),
                )
            elif filter_type == "measurement":
                current_expression = self.add_measurement_filter(
                    current_expression,
                    filter_def.get("concept_set_id"),
                    filter_def.get("value_min"),
                    filter_def.get("value_max"),
                    filter_def.get("unit_concept_id"),
                    filter_def.get("days_before", 365),
                    filter_def.get("days_after", 0),
                    filter_def.get("filter_name"),
                )
            elif filter_type == "drug_era":
                current_expression = self.add_drug_era_filter(
                    current_expression,
                    filter_def.get("concept_set_id"),
                    filter_def.get("era_length_min"),
                    filter_def.get("era_length_max"),
                    filter_def.get("days_before", 365),
                    filter_def.get("days_after", 0),
                    filter_def.get("filter_name"),
                )
            elif filter_type == "prior_observation":
                current_expression = self.add_prior_observation_filter(current_expression, filter_def.get("min_days", 365))
            elif filter_type == "multiple_conditions":
                current_expression = self.add_multiple_conditions_filter(
                    current_expression,
                    filter_def.get("concept_set_ids", []),
                    filter_def.get("logic", "ALL"),
                    filter_def.get("days_before", 365),
                    filter_def.get("days_after", 0),
                    filter_def.get("filter_name"),
                )

            # Create and generate cohort with current filters
            step_cohort = CohortDefinition(
                name=f"{base_name} - Step {step_num}: {filter_def.get('name', filter_type)}", expression=current_expression
            )

            created_step = self.create(step_cohort)
            self.generate(created_step.id, source_key)
            self.poll_generation(created_step.id, source_key)
            step_counts = self.counts(created_step.id)
            step_subject_count = step_counts[0].subject_count if step_counts else 0
            results.append((created_step, step_subject_count))
            step_num += 1

        # Apply exclusion criteria incrementally
        if exclusions:
            for exclusion_def in exclusions:
                exclusion_type = exclusion_def.get("type")

                if exclusion_type == "condition":
                    current_expression = self.add_exclusion_condition(
                        current_expression,
                        exclusion_def.get("concept_set_id"),
                        exclusion_def.get("days_before", 365),
                        exclusion_def.get("days_after", 0),
                        exclusion_def.get("name"),
                    )
                elif exclusion_type == "drug":
                    current_expression = self.add_exclusion_drug(
                        current_expression,
                        exclusion_def.get("concept_set_id"),
                        exclusion_def.get("days_before", 365),
                        exclusion_def.get("days_after", 0),
                        exclusion_def.get("name"),
                    )
                elif exclusion_type == "procedure":
                    current_expression = self.add_exclusion_procedure(
                        current_expression,
                        exclusion_def.get("concept_set_id"),
                        exclusion_def.get("days_before", 365),
                        exclusion_def.get("days_after", 0),
                        exclusion_def.get("name"),
                    )
                elif exclusion_type == "death":
                    current_expression = self.add_exclusion_death(current_expression, exclusion_def.get("days_after_index", 30))

                # Create and generate cohort with current exclusions
                step_cohort = CohortDefinition(
                    name=f"{base_name} - Step {step_num}: Exclude {exclusion_def.get('name', exclusion_type)}",
                    expression=current_expression,
                )

                created_step = self.create(step_cohort)
                self.generate(created_step.id, source_key)
                self.poll_generation(created_step.id, source_key)
                step_counts = self.counts(created_step.id)
                step_subject_count = step_counts[0].subject_count if step_counts else 0
                results.append((created_step, step_subject_count))
                step_num += 1

        return results
