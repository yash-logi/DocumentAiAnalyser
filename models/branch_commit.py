"""Pydantic models for branch and commit history analysis."""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BranchItem(BaseModel):
    """Representation of a Git branch."""
    name: str
    is_default: bool = False
    is_protected: bool = False
    latest_commit_sha: str = ""
    is_active: bool = True
    days_since_commit: Optional[int] = None


class CommitItem(BaseModel):
    """Representation of a Git commit."""
    sha: str
    message: str
    author: str
    date: datetime
    url: Optional[str] = None
    files_modified: List[str] = Field(default_factory=list)


class BranchCommitData(BaseModel):
    """Aggregated branch, commit history, and velocity trends."""
    total_branches: int = 0
    active_branches: List[str] = Field(default_factory=list)
    stale_branches: List[str] = Field(default_factory=list)
    recent_commits: List[str] = Field(default_factory=list)
    commit_frequency_summary: str = "Active"
    frequently_modified_files: List[str] = Field(default_factory=list)
    top_contributors: List[str] = Field(default_factory=list)
    velocity_trends: str = "Steady"
