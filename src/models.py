"""
Pydantic data models used throughout the AI Resume Screening system.

This module contains the shared data structures passed between:
- Resume ingestion
- Candidate extraction
- Eligibility filtering
- Candidate scoring
- GitHub enrichment
- Pipeline orchestration
"""

from pydantic import BaseModel, Field


class RawResume(BaseModel):
    """Represents the raw result of reading one resume file."""

    filename: str
    raw_text: str = ""
    parse_success: bool
    parse_error: str | None = None
    is_duplicate: bool = False


class ProjectEntry(BaseModel):
    """Represents a project extracted from a candidate's resume."""

    title: str
    description: str
    technologies: list[str] = Field(default_factory=list)


class CandidateProfile(BaseModel):
    """Structured candidate information extracted from a resume."""

    name: str
    email: str | None = None
    phone: str | None = None
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    github_url: str | None = None
    raw_text: str = ""


class EligibilityResult(BaseModel):
    """Result of the hard Python + AI/agentic eligibility filter."""

    candidate: CandidateProfile
    eligible: bool
    rejection_reasons: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    """100-point scoring breakdown for an eligible candidate."""

    ai_project_depth: int = Field(ge=0, le=40)
    python_backend: int = Field(ge=0, le=30)
    cloud_fullstack: int = Field(ge=0, le=15)
    github: int = Field(ge=0, le=10)
    engineering_depth: int = Field(ge=0, le=5)

    total_score: int = Field(ge=0, le=100)

    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)


class GithubEnrichment(BaseModel):
    """Represents the result of GitHub profile enrichment."""

    status: str
    score: int = Field(ge=0, le=10)
    summary: str


class BatchSummary(BaseModel):
    """Summary of processing results for the complete resume batch."""

    total_resumes: int
    successfully_parsed: int
    eligible: int
    rejected: int
    failed_unreadable: int