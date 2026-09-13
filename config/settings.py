"""Configuration module for Agentic GitHub Repository Analyzer."""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable and .env support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # GitHub Credentials & API
    github_token: Optional[str] = Field(
        default=None,
        description="GitHub personal access token for higher rate limits and private repo access"
    )
    github_api_base: str = Field(
        default="https://api.github.com",
        description="Base URL for GitHub REST API"
    )

    # LLM Settings
    llm_api_key: Optional[str] = Field(
        default=None,
        description="API key for LLM provider (OpenAI, Gemini, Anthropic, etc.)"
    )
    llm_model: str = Field(
        default="gpt-4o-mini",
        description="Model name for CrewAI agents (e.g. gpt-4o-mini, gemini-1.5-flash)"
    )
    llm_api_base: Optional[str] = Field(
        default=None,
        description="Custom API Base URL if using proxies or local models"
    )

    # GitHub MCP Settings
    mcp_enabled: bool = Field(
        default=True,
        description="Whether to attempt GitHub MCP integration"
    )
    mcp_server_command: Optional[str] = Field(
        default=None,
        description="Command to run GitHub MCP server via stdio"
    )

    # System & Execution Settings
    output_dir: Path = Field(
        default=Path("reports"),
        description="Directory where Markdown, XHTML, and diagram reports are saved"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR"
    )
    request_timeout: float = Field(
        default=25.0,
        description="Timeout in seconds for HTTP requests"
    )
    max_issues_to_fetch: int = Field(
        default=50,
        description="Maximum issues to fetch for analysis"
    )
    max_prs_to_fetch: int = Field(
        default=30,
        description="Maximum pull requests to fetch for analysis"
    )
    max_commits_to_fetch: int = Field(
        default=50,
        description="Maximum commits to fetch for analysis"
    )
    max_files_for_ast: int = Field(
        default=60,
        description="Maximum code files to parse with AST to prevent memory/token exhaustion"
    )

    @property
    def markdown_dir(self) -> Path:
        p = self.output_dir / "markdown"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def xhtml_dir(self) -> Path:
        p = self.output_dir / "xhtml"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def diagrams_dir(self) -> Path:
        p = self.output_dir / "diagrams"
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
