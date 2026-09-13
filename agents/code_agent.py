"""Agent 5: Code Structure Agent."""

from typing import Optional, Any
from crewai import Agent

def create_code_agent(llm: Optional[Any] = None) -> Agent:
    """Creates the Codebase Architect agent."""
    return Agent(
        role="Codebase Architect",
        goal="Analyze repository modules, parse AST hierarchies for classes, functions, internal and external imports, and identify entry points.",
        backstory=(
            "You are a principal systems architect specializing in static code analysis and module "
            "decomposition. You examine how code is partitioned, identifying core domain logic, "
            "auxiliary utilities, and separation of concerns across languages."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
