"""Pydantic models for pull request analysis."""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PullRequestItem(BaseModel):
    """Representation of an individual GitHub pull request."""
    number: int
    title: str
    state: str
    is_merged: bool = False
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    author: str = "unknown"
    additions: int = 0
    deletions: int = 0
    changed_files_count: int = 0
    labels: List[str] = Field(default_factory=list)
    changed_file_names: List[str] = Field(default_factory=list)
    body_snippet: Optional[str] = None


class PRAnalysisData(BaseModel):
    """Aggregated pull request analytics and risk assessment."""
    total_prs_analyzed: int = 0
    open_prs: int = 0
    merged_prs: int = 0
    closed_unmerged_prs: int = 0
    important_prs: List[str] = Field(default_factory=list)
    risky_changes: List[str] = Field(default_factory=list)
    frequently_changed_files: List[str] = Field(default_factory=list)
    stale_prs: List[str] = Field(default_factory=list)
    development_trends: str = "Regular merge cadence"
