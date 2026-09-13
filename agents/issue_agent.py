"""Agent 2: Issue Analysis Agent."""

from typing import Optional, Any
from crewai import Agent

def create_issue_agent(llm: Optional[Any] = None) -> Agent:
    """Creates the GitHub Issue Analyst agent."""
    return Agent(
        role="GitHub Issue Analyst",
        goal="Analyze open and closed issues, detect recurring bugs, triage feature requests, determine issue priorities, and identify systemic trends.",
        backstory=(
            "You are a senior QA lead and issue triage director. You excel at categorizing "
            "bug reports, spotting developer bottlenecks, detecting flaky components, and "
            "prioritizing community feedback into actionable work items."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
