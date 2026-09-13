"""Agent 7: Repository Intelligence Agent."""

from typing import Optional, Any
from crewai import Agent

def create_intelligence_agent(llm: Optional[Any] = None) -> Agent:
    """Creates the Senior Software Engineer agent."""
    return Agent(
        role="Senior Software Engineer",
        goal="Combine findings from all domain agents to evaluate overall health, detect technical debt, assess security and testing risks, and recommend prioritized remedies.",
        backstory=(
            "You are a Distinguished Software Engineer and technical advisor who has evaluated hundreds "
            "of production systems. You provide sober, factual, and deeply actionable technical advice, "
            "clearly separating confirmed facts from inferences, with zero hallucination."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
