from __future__ import annotations

from pydantic import BaseModel, Field


class WebApiInfo(BaseModel):
    version: str | None = None
    build_date: str | None = Field(default=None, alias="buildDate")
    git_commit_id: str | None = Field(default=None, alias="gitCommitId")
