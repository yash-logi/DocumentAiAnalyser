"""Agent 1: Repository Discovery Agent."""

from typing import Optional, Any
from crewai import Agent

def create_repository_agent(llm: Optional[Any] = None) -> Agent:
    """Creates the Repository Explorer agent."""
    return Agent(
        role="Repository Explorer",
        goal="Validate GitHub repository URL, inspect project structure, identify primary languages, manifest files, configuration, and entry points.",
        backstory=(
            "You are a seasoned software cataloger and repository reconnaissance expert. "
            "You meticulously inspect file trees, manifests, and project configurations "
            "to understand the foundational anatomy of open-source and proprietary software."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
