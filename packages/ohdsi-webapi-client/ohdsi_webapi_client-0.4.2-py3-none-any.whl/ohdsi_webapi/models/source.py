from __future__ import annotations

from pydantic import BaseModel, Field


class SourceDaimon(BaseModel):
    daimon_type: str = Field(alias="daimonType")
    table_qualifier: str | None = Field(default=None, alias="tableQualifier")
    priority: int | None = None


class Source(BaseModel):
    source_id: int = Field(alias="sourceId")
    source_name: str = Field(alias="sourceName")
    source_key: str = Field(alias="sourceKey")
    source_dialect: str = Field(alias="sourceDialect")
    daimons: list[SourceDaimon] = []
