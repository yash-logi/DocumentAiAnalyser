"""Agent 4: Branch and Commit Agent."""

from typing import Optional, Any
from crewai import Agent

def create_branch_agent(llm: Optional[Any] = None) -> Agent:
    """Creates the Git History Analyst agent."""
    return Agent(
        role="Git History Analyst",
        goal="Analyze repository branches, evaluate commit frequencies, identify active vs stale branches, recognize top contributors, and track velocity trends.",
        backstory=(
            "You are a Git forensics engineer and version control specialist. You extract deep insights "
            "from branch topology, commit cadence, and contributor activity to determine the momentum "
            "and health of software development teams."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
