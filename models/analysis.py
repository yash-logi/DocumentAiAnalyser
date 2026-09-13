"""Pydantic models for dependency graphs, intelligence synthesis, and final reports."""

from typing import List, Dict, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from models.repository import RepositoryOverview
from models.issue import IssueAnalysisData
from models.pull_request import PRAnalysisData
from models.branch_commit import BranchCommitData
from models.code_structure import CodeStructureData


class DependencyNode(BaseModel):
    """Graph node representing a module or component."""
    id: str
    label: str
    node_type: str = "module"  # entry_point, service, model, tool, external


class DependencyEdge(BaseModel):
    """Directed dependency link between modules."""
    source: str
    target: str
    relationship: str = "imports"  # imports, calls, depends_on


class DependencyGraphData(BaseModel):
    """Dependency analysis results and Mermaid representation."""
    nodes: List[DependencyNode] = Field(default_factory=list)
    edges: List[DependencyEdge] = Field(default_factory=list)
    mermaid_diagram: str = "flowchart TD\n  Start[Application] --> Core[Module]"
    entry_point_nodes: List[str] = Field(default_factory=list)
    leaf_nodes: List[str] = Field(default_factory=list)
    isolated_nodes: List[str] = Field(default_factory=list)
    circular_dependencies: List[str] = Field(default_factory=list)
    architectural_pattern: str = "Modular Architecture"


class ActionRecommendation(BaseModel):
    """Structured actionable recommendation."""
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    category: str = "General"  # Security, Architecture, Testing, Maintenance, Documentation
    description: str
    rationale: str
    suggested_fix: Optional[str] = None


class IntelligenceSummary(BaseModel):
    """Senior software engineer holistic evaluation."""
    repository_health_score: int = 80  # 0 to 100
    health_status: str = "Good"  # Excellent, Good, Fair, Needs Attention, Critical
    executive_summary: str
    development_activity_summary: str
    issue_trends: str
    pr_trends: str
    branch_activity_summary: str
    code_architecture_evaluation: str
    potential_technical_debt: List[str] = Field(default_factory=list)
    potential_risks: List[str] = Field(default_factory=list)
    documentation_quality: str
    testing_situation: str
    dependency_concerns: List[str] = Field(default_factory=list)
    maintainability_score: str = "High"
    recommendations_high: List[ActionRecommendation] = Field(default_factory=list)
    recommendations_medium: List[ActionRecommendation] = Field(default_factory=list)
    recommendations_low: List[ActionRecommendation] = Field(default_factory=list)


class HowToRunPlan(BaseModel):
    """Inferred local setup and execution instructions."""
    confidence_label: str = "Likely execution procedure"
    prerequisites: List[str] = Field(default_factory=list)
    installation_steps: List[str] = Field(default_factory=list)
    configuration_steps: List[str] = Field(default_factory=list)
    execution_steps: List[str] = Field(default_factory=list)
    detected_manifests: List[str] = Field(default_factory=list)
    notes_and_warnings: List[str] = Field(default_factory=list)


class CompleteAnalysisReport(BaseModel):
    """Unified data model feeding Markdown and XHTML report generation."""
    repository_name: str
    overview: RepositoryOverview
    issue_data: IssueAnalysisData
    pr_data: PRAnalysisData
    git_data: BranchCommitData
    code_data: CodeStructureData
    dependency_data: DependencyGraphData
    intelligence: IntelligenceSummary
    how_to_run: HowToRunPlan
    markdown_path: Optional[str] = None
    xhtml_path: Optional[str] = None
    diagram_path: Optional[str] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: float = 0.0
