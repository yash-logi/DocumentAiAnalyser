"""CrewAI agents builder with configurable LLM provider support."""

import os
import logging
from typing import Optional, Dict, Any
from crewai import Agent, LLM

from config.settings import settings
import agents

logger = logging.getLogger("agentic_github_analyzer.crew.agents")


def get_llm_instance() -> Optional[LLM]:
    """Initialize LLM instance based on environment settings if API key is present."""
    api_key = settings.llm_api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.info("[INFO] No LLM API key detected. Operating in Deterministic Heuristic mode.")
        return None

    try:
        model_name = settings.llm_model
        # Configure CrewAI LLM
        kwargs: Dict[str, Any] = {"model": model_name, "api_key": api_key}
        if settings.llm_api_base:
            kwargs["base_url"] = settings.llm_api_base

        llm = LLM(**kwargs)
        logger.info(f"[INFO] Initialized LLM provider for model: {model_name}")
        return llm
    except Exception as e:
        logger.warning(f"[WARNING] Could not initialize LLM ({e}). Falling back to deterministic mode.")
        return None


class RepositoryCrewAgents:
    """Instantiates all 8 CrewAI agents."""

    def __init__(self, llm: Optional[LLM] = None):
        self.llm = llm if llm is not None else get_llm_instance()

        self.repository_agent = agents.create_repository_agent(self.llm)
        self.issue_agent = agents.create_issue_agent(self.llm)
        self.pr_agent = agents.create_pr_agent(self.llm)
        self.branch_agent = agents.create_branch_agent(self.llm)
        self.code_agent = agents.create_code_agent(self.llm)
        self.dependency_agent = agents.create_dependency_agent(self.llm)
        self.intelligence_agent = agents.create_intelligence_agent(self.llm)
        self.report_agent = agents.create_report_agent(self.llm)
