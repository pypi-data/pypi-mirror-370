from __future__ import annotations

from pydantic import BaseModel, Field


class Concept(BaseModel):
    concept_id: int = Field(alias="conceptId")
    concept_name: str = Field(alias="conceptName")
    vocabulary_id: str | None = Field(default=None, alias="vocabularyId")
    concept_class_id: str | None = Field(default=None, alias="conceptClassId")
    standard_concept: str | None = Field(default=None, alias="standardConcept")
    concept_code: str | None = Field(default=None, alias="conceptCode")
    domain_id: str | None = Field(default=None, alias="domainId")
    valid_start_date: str | None = Field(default=None, alias="validStartDate")
    valid_end_date: str | None = Field(default=None, alias="validEndDate")
    invalid_reason: str | None = Field(default=None, alias="invalidReason")


class ConceptAncestor(BaseModel):
    ancestor_concept_id: int = Field(alias="ancestorConceptId")
    descendant_concept_id: int = Field(alias="descendantConceptId")
    min_levels_of_separation: int | None = Field(default=None, alias="minLevelsOfSeparation")
    max_levels_of_separation: int | None = Field(default=None, alias="maxLevelsOfSeparation")
