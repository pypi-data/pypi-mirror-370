from __future__ import annotations

from typing import Any

from ohdsi_cohort_schemas import ConceptSetExpression
from pydantic import BaseModel, Field

# WebAPI-specific models that add metadata not in core schemas


class ConceptSet(BaseModel):
    """WebAPI concept set with optional expression (for CRUD operations)."""

    id: int | None = None
    name: str
    oid: int | None = None
    tags: list[Any] | None = None
    expression: ConceptSetExpression | dict | None = None  # Optional for WebAPI CRUD


class WebApiConceptSetItem(BaseModel):
    """A concept set item as returned by /conceptset/{id}/items endpoint."""

    id: int
    concept_set_id: int = Field(alias="conceptSetId")
    concept_id: int = Field(alias="conceptId")
    is_excluded: int = Field(alias="isExcluded")  # 0 or 1 in API
    include_descendants: int = Field(alias="includeDescendants")  # 0 or 1 in API
    include_mapped: int | None = Field(default=None, alias="includeMapped")  # 0 or 1 in API

    @property
    def is_excluded_bool(self) -> bool:
        """Convert is_excluded integer to boolean."""
        return bool(self.is_excluded)

    @property
    def include_descendants_bool(self) -> bool:
        """Convert include_descendants integer to boolean."""
        return bool(self.include_descendants)

    @property
    def include_mapped_bool(self) -> bool:
        """Convert include_mapped integer to boolean."""
        return bool(self.include_mapped) if self.include_mapped is not None else False


class ResolvedConceptSetItem(BaseModel):
    """A resolved concept set item with concept details."""

    conceptId: int
    conceptName: str
    isExcluded: bool | None = None
    includeDescendants: bool | None = None
    includeMapped: bool | None = None
    # Additional fields may appear; store raw
    additionalFields: dict | None = None
