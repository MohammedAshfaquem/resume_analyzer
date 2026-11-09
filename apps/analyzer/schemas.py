from typing import Literal

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    requirement: str = Field(min_length=1, max_length=300)
    job_evidence: str = Field(min_length=1, max_length=1500)
    importance: Literal["required", "preferred"]
    status: Literal["supported", "partial", "missing", "unclear"]
    resume_evidence: str = Field(max_length=1500)
    explanation: str = Field(min_length=1, max_length=1200)
    action: str = Field(min_length=1, max_length=1200)


class Rewrite(BaseModel):
    original: str = Field(min_length=1, max_length=1500)
    suggested: str = Field(min_length=1, max_length=2000)


class Analysis(BaseModel):
    role: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=2000)
    requirements: list[Requirement] = Field(min_length=1, max_length=60)
    improvements: list[str] = Field(max_length=8)
    rewrites: list[Rewrite] = Field(max_length=5)
