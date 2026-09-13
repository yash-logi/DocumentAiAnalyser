"""Pydantic models for repository metadata and structural discovery."""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RepositoryRef(BaseModel):
    """Parsed repository reference."""
    owner: str = Field(..., description="Repository owner/organization")
    repo: str = Field(..., description="Repository name")
    original_url: str = Field(..., description="Supplied repository URL")

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"


class RepositoryMetadata(BaseModel):
    """Raw and processed GitHub repository metadata."""
    name: str
    full_name: str
    description: Optional[str] = None
    default_branch: str = "main"
    stars_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    subscribers_count: int = 0
    license_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    pushed_at: Optional[datetime] = None
    is_private: bool = False
    is_archived: bool = False
    is_fork: bool = False
    homepage: Optional[str] = None
    topics: List[str] = Field(default_factory=list)


class RepositoryStructure(BaseModel):
    """Discovered structure, languages, configuration, and entry points."""
    repository: str
    languages: List[str] = Field(default_factory=list)
    language_distribution: Dict[str, int] = Field(default_factory=dict)
    important_directories: List[str] = Field(default_factory=list)
    config_files: List[str] = Field(default_factory=list)
    entry_points: List[str] = Field(default_factory=list)
    manifest_files: List[str] = Field(default_factory=list)
    readme_present: bool = False
    readme_path: Optional[str] = None
    docker_present: bool = False
    ci_cd_present: bool = False
    total_files_scanned: int = 0


class RepositoryOverview(BaseModel):
    """Full discovery overview combining metadata and structure."""
    metadata: RepositoryMetadata
    structure: RepositoryStructure
