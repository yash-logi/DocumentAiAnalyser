"""Pydantic models for issue analysis."""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class IssueItem(BaseModel):
    """Representation of an individual GitHub issue."""
    number: int
    title: str
    state: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    author: str = "unknown"
    labels: List[str] = Field(default_factory=list)
    comments_count: int = 0
    is_pull_request: bool = False
    body_snippet: Optional[str] = None


class IssueAnalysisData(BaseModel):
    """Aggregated issue analytics and categorized findings."""
    total_issues_analyzed: int = 0
    open_issues: int = 0
    closed_issues: int = 0
    major_bugs: List[str] = Field(default_factory=list)
    feature_requests: List[str] = Field(default_factory=list)
    recurring_problems: List[str] = Field(default_factory=list)
    unresolved_issues: List[str] = Field(default_factory=list)
    priority_breakdown: Dict[str, int] = Field(default_factory=lambda: {"high": 0, "medium": 0, "low": 0})
    recommended_actions: List[str] = Field(default_factory=list)
    trends: str = "Stable"
