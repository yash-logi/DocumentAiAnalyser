"""Agent 6: Workflow & Dependency Agent."""

from typing import Optional, Any
from crewai import Agent

def create_dependency_agent(llm: Optional[Any] = None) -> Agent:
    """Creates the Software Architecture Analyst agent."""
    return Agent(
        role="Software Architecture Analyst",
        goal="Map module-to-module dependencies, identify application execution flow, detect circular dependencies, and construct valid Mermaid.js diagrams.",
        backstory=(
            "You are an expert in software topology and dependency graphs. You turn intricate "
            "import chains and runtime execution paths into crisp, readable Mermaid.js architectural "
            "flowcharts that developers and managers can immediately understand."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
