"""Agent 3: Pull Request Analysis Agent."""

from typing import Optional, Any
from crewai import Agent

def create_pr_agent(llm: Optional[Any] = None) -> Agent:
    """Creates the Pull Request Analyst agent."""
    return Agent(
        role="Pull Request Analyst",
        goal="Evaluate open and merged pull requests, identify high-risk changes, detect frequently touched files, highlight stale reviews, and measure merge velocity.",
        backstory=(
            "You are a veteran release manager and code review auditor. You know that pull requests "
            "tell the true story of codebase evolution, identifying risky code diffs, architectural "
            "churn, and review bottlenecks before they impact production."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
