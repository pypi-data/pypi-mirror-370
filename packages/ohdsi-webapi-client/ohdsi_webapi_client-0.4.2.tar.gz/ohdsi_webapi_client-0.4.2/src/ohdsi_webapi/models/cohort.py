from __future__ import annotations

import json
from typing import Any

from ohdsi_cohort_schemas import CohortExpression
from pydantic import BaseModel, Field, field_validator


class CohortSubject(BaseModel):
    subject_id: int = Field(alias="subjectId")
    cohort_start_date: str = Field(alias="cohortStartDate")
    cohort_end_date: str = Field(alias="cohortEndDate")
    cohort_definition_id: int = Field(alias="cohortDefinitionId")


class CohortDefinition(BaseModel):
    id: int | None = None
    name: str
    description: str | None = None
    expression_type: str = Field(default="SIMPLE_EXPRESSION", alias="expressionType")
    expression: CohortExpression | dict[str, Any] | None = None

    @field_validator("expression", mode="before")
    @classmethod
    def parse_expression(cls, v):
        if isinstance(v, str):
            try:
                data = json.loads(v)
                # Try to parse as CohortExpression, but fall back to dict if it fails
                try:
                    return CohortExpression.model_validate(data)
                except ValueError:
                    return data
            except (json.JSONDecodeError, ValueError):
                return None
        elif isinstance(v, dict):
            # Try to parse as CohortExpression, but fall back to dict if it fails
            try:
                return CohortExpression.model_validate(v)
            except ValueError:
                # Return the dict as-is if CohortExpression validation fails
                return v
        return v

    def model_dump(self, **kwargs):
        """Override model_dump to handle mixed expression types properly."""
        data = super().model_dump(**kwargs)

        # If expression is a CohortExpression object, convert it to dict
        if isinstance(self.expression, CohortExpression):
            data["expression"] = self.expression.model_dump(
                by_alias=kwargs.get("by_alias", False), exclude_none=kwargs.get("exclude_none", False)
            )

        return data


class CohortGenerationRequest(BaseModel):
    # structure may include various settings; keep flexible
    id: int
    source_key: str = Field(alias="sourceKey")


class JobStatus(BaseModel):
    execution_id: int | None = Field(default=None, alias="executionId")
    status: str
    start_time: str | None = Field(default=None, alias="startTime")
    end_time: str | None = Field(default=None, alias="endTime")


class InclusionRuleStats(BaseModel):
    id: int
    name: str
    count: int
    person_count: int = Field(alias="personCount")


class CohortCount(BaseModel):
    cohort_definition_id: int = Field(alias="cohortDefinitionId")
    subject_count: int = Field(alias="subjectCount")
    entry_count: int = Field(alias="entryCount")
