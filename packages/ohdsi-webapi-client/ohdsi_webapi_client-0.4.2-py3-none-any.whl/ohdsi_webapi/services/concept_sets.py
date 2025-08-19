from __future__ import annotations

from typing import Any, Iterable, Iterator

from ..cache import cached_method
from ..http import HttpExecutor
from ..models.concept_set import ConceptSet, WebApiConceptSetItem


class ConceptSetService:
    """Service for managing OMOP concept sets.

    Concept sets are collections of OMOP concepts that represent clinical entities
    (like "Type 2 Diabetes" or "ACE Inhibitors"). They are fundamental building
    blocks for cohort definitions and can be reused across multiple studies.
    """

    def __init__(self, http: HttpExecutor):
        self._http = http

    @cached_method(ttl_seconds=3600)  # 1 hour for expensive list operation (20K+ items)
    def list(self, *, force_refresh: bool = False) -> list[ConceptSet]:
        """List all concept sets (metadata only).

        This method is automatically cached to improve performance since the WebAPI
        endpoint returns ALL concept sets (often 20,000+ items) without pagination.

        Parameters
        ----------
        force_refresh : bool, default False
            If True, bypass cache and fetch fresh data from the server.

        Returns
        -------
        list of ConceptSet
            All available concept sets with metadata only (no expressions).
            Use get() to retrieve full details including expressions.

        Warning
        -------
        This endpoint returns ALL concept sets without pagination.
        On busy servers, this can be 20,000+ items. Consider using list_filtered()
        for common filtering needs or iter_all() for memory-efficient processing.

        Examples
        --------
        >>> # Get all concept sets (metadata only)
        >>> all_sets = client.concept_sets.list()
        >>> print(f"Total concept sets: {len(all_sets)}")
        >>>
        >>> # Force refresh from server
        >>> fresh_sets = client.concept_sets.list(force_refresh=True)
        """
        data = self._http.get("/conceptset/")
        if isinstance(data, list):
            out: list[ConceptSet] = []
            for d in data:
                if isinstance(d, dict):
                    # Exclude expression field for list view - use get() for full details
                    metadata = {k: v for k, v in d.items() if k in {"id", "name", "oid", "tags"}}
                    out.append(ConceptSet(**metadata))
            return out
        return []

    def list_filtered(self, name_contains: str | None = None, limit: int | None = None, tags: list[str] | None = None) -> list[ConceptSet]:
        """List concept sets with client-side filtering.

        Args:
            name_contains: Filter by concept sets whose name contains this string (case-insensitive)
            limit: Maximum number of results to return
            tags: Filter by concept sets that have any of these tags

        Returns:
            Filtered list of concept sets (metadata only)

        Example:
            # Find concept sets related to diabetes, limit to 10
            diabetes_sets = client.concept_sets.list_filtered(name_contains="diabetes", limit=10)
        """
        all_sets = self.list()

        # Apply name filter
        if name_contains:
            name_lower = name_contains.lower()
            all_sets = [cs for cs in all_sets if name_lower in (cs.name or "").lower()]

        # Apply tags filter
        if tags:
            tags_lower = [tag.lower() for tag in tags]
            all_sets = [
                cs
                for cs in all_sets
                if cs.tags and any(any(tag_filter in (tag or "").lower() for tag_filter in tags_lower) for tag in cs.tags)
            ]

        # Apply limit
        if limit and limit > 0:
            all_sets = all_sets[:limit]

        return all_sets

    def iter_all(self) -> Iterator[ConceptSet]:
        """Iterate through all concept sets, yielding full details on demand.

        This is memory-efficient for processing large numbers of concept sets
        since it fetches the full expression only when each item is accessed.

        Yields:
            ConceptSet objects with full details including expressions

        Example:
            # Process all concept sets without loading everything into memory
            for concept_set in client.concept_sets.iter_all():
                if len(concept_set.expression.get('items', [])) > 100:
                    print(f"Large concept set: {concept_set.name}")
        """
        for cs_metadata in self.list():
            # Fetch full details on demand
            yield self.get(cs_metadata.id)

    @cached_method(ttl_seconds=1800)  # 30 minutes for individual concept sets
    def get(self, concept_set_id: int, *, force_refresh: bool = False) -> ConceptSet:
        """Get a concept set by ID with full details including expression.

        Args:
            concept_set_id: The concept set ID to retrieve
            force_refresh: If True, bypass cache and fetch fresh data
        """
        data = self._http.get(f"/conceptset/{concept_set_id}")
        if isinstance(data, dict):
            return ConceptSet(**data)
        raise ValueError("Unexpected concept set response")

    def create(self, name: str, expression: dict | None = None) -> ConceptSet:
        payload = {"name": name}
        if expression:
            payload["expression"] = expression
        data = self._http.post("/conceptset/", json_body=payload)
        if isinstance(data, dict):
            return ConceptSet(**data)
        raise ValueError("Unexpected create concept set response")

    def update(self, concept_set: ConceptSet) -> ConceptSet:
        if concept_set.id is None:
            raise ValueError("ConceptSet id required for update")
        data = self._http.put(f"/conceptset/{concept_set.id}", json_body=concept_set.model_dump())
        if isinstance(data, dict):
            return ConceptSet(**data)
        raise ValueError("Unexpected update concept set response")

    def delete(self, concept_set_id: int) -> None:
        self._http.delete(f"/conceptset/{concept_set_id}")

    def expression(self, concept_set_id: int) -> dict:
        data = self._http.get(f"/conceptset/{concept_set_id}/expression")
        return data if isinstance(data, dict) else {}

    def set_expression(self, concept_set_id: int, expression: dict) -> dict:
        """Replace the concept set expression without altering other metadata.
        POST /conceptset/{id}/expression returns updated expression structure.
        """
        data = self._http.post(f"/conceptset/{concept_set_id}/expression", json_body=expression)
        return data if isinstance(data, dict) else {}

    @cached_method(ttl_seconds=1800)  # 30 minutes for concept set resolution
    def resolve(self, concept_set_id: int) -> list[WebApiConceptSetItem]:
        """Get the concept set items (concepts) in a concept set.

        This method retrieves the concept set items that define which concepts
        are included or excluded from the concept set. Note that this returns
        the raw concept set items, not the fully resolved concepts with names.

        Parameters
        ----------
        concept_set_id : int
            The ID of the concept set to get items for.

        Returns
        -------
        list[WebApiConceptSetItem]
            List of concept set items showing concept IDs and inclusion rules.

        Examples
        --------
        >>> items = client.concept_sets.resolve(123)
        >>> for item in items:
        ...     print(f"Concept {item.concept_id}: excluded={item.is_excluded}")
        """
        data = self._http.get(f"/conceptset/{concept_set_id}/items")
        if isinstance(data, list):
            return [WebApiConceptSetItem(**d) for d in data if isinstance(d, dict)]
        return []

    def resolve_many(self, concept_set_ids: Iterable[int]) -> dict[int, list[WebApiConceptSetItem]]:
        """Get concept set items for multiple concept sets in batch.

        This is an optimized method for retrieving items from multiple concept sets
        at once, which can be more efficient than making individual calls.

        Parameters
        ----------
        concept_set_ids : Iterable[int]
            The IDs of the concept sets to get items for.

        Returns
        -------
        dict[int, list[WebApiConceptSetItem]]
            Dictionary mapping concept set ID to list of concept set items.

        Examples
        --------
        >>> items_by_cs = client.concept_sets.resolve_many([123, 456])
        >>> print(f"CS 123 has {len(items_by_cs[123])} items")
        """
        # For now, just make individual calls
        # Future optimization: check if WebAPI supports batch resolve
        result: dict[int, list[WebApiConceptSetItem]] = {}
        for concept_set_id in concept_set_ids:
            result[concept_set_id] = self.resolve(concept_set_id)
        return result

    def generation_info(self, concept_set_id: int) -> list[dict[str, Any]]:
        """Return generation info metadata if available (usage stats, counts)."""
        data = self._http.get(f"/conceptset/{concept_set_id}/generationinfo")
        return data if isinstance(data, list) else []

    def export(self, concept_set_id: int, format: str = "csv") -> str:
        """Export the concept set. Common formats: 'csv', 'json'. Returns raw text/JSON string."""
        endpoint = f"/conceptset/{concept_set_id}/export"
        params = {"format": format} if format else None
        data = self._http.get(endpoint, params=params)
        # If JSON structured, stringify
        if isinstance(data, (dict, list)):
            import json

            return json.dumps(data)
        return str(data)

    def included_concepts(self, concept_set_id: int) -> list[dict[str, Any]]:
        """Fetch included concepts (if endpoint available). Tries several variants; returns empty list if unsupported."""
        candidates = [
            f"/conceptset/{concept_set_id}/includedConcepts",
            f"/conceptset/{concept_set_id}/included-concepts",
        ]
        for ep in candidates:
            try:
                data = self._http.get(ep)
            except Exception:
                continue
            if isinstance(data, list):
                return data
        return []
