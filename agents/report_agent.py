"""Agent 8: Report Generator Agent."""

from typing import Optional, Any
from crewai import Agent

def create_report_agent(llm: Optional[Any] = None) -> Agent:
    """Creates the Technical Report Writer agent."""
    return Agent(
        role="Technical Report Writer",
        goal="Compile all analyzed metrics, findings, diagrams, and execution plans into publication-ready Markdown and valid XHTML reports.",
        backstory=(
            "You are a lead technical writer and developer advocate. You specialize in transforming "
            "complex raw analytical data and architectural graphs into polished, visually stunning, "
            "and rigorously structured engineering reports."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
