"""CrewAI task definitions for the repository analysis pipeline."""

from crewai import Task, Agent

class RepositoryCrewTasks:
    """Creates individual tasks mapped to each specialized agent."""

    @staticmethod
    def discovery_task(agent: Agent, repo_context: str) -> Task:
        return Task(
            description=(
                f"Inspect the repository structure and configuration.\n"
                f"Context:\n{repo_context}\n"
                "Verify languages, manifest files, entry points, and directory layout. "
                "Output a clear, factual summary of the discovered structure."
            ),
            expected_output="Structured overview detailing languages, configuration files, and entry points.",
            agent=agent
        )

    @staticmethod
    def issue_analysis_task(agent: Agent, issue_context: str) -> Task:
        return Task(
            description=(
                f"Analyze the repository's open and closed issues.\n"
                f"Issue Data:\n{issue_context}\n"
                "Identify major recurring bugs, feature request frequency, triage priority, and resolution trends. "
                "Distinguish between verified facts and inferences."
            ),
            expected_output="Categorized issue summary highlighting major bugs, feature requests, and resolution trends.",
            agent=agent
        )

    @staticmethod
    def pr_analysis_task(agent: Agent, pr_context: str) -> Task:
        return Task(
            description=(
                f"Analyze the pull requests and code churn.\n"
                f"PR Data:\n{pr_context}\n"
                "Examine merged and open PRs, pinpoint high-risk changes, frequently modified files, "
                "and identify any stale reviews or merge bottlenecks."
            ),
            expected_output="Pull request evaluation including risky changes, churn hotspots, and merge cadence.",
            agent=agent
        )

    @staticmethod
    def git_history_task(agent: Agent, git_context: str) -> Task:
        return Task(
            description=(
                f"Analyze the branch topology and commit history.\n"
                f"Git Data:\n{git_context}\n"
                "Determine active vs stale branches, commit frequency, and top contributors."
            ),
            expected_output="Git history analysis with branch activity, commit velocity, and contributor activity.",
            agent=agent
        )

    @staticmethod
    def code_structure_task(agent: Agent, code_context: str) -> Task:
        return Task(
            description=(
                f"Analyze the repository source code hierarchy and AST symbols.\n"
                f"Code Data:\n{code_context}\n"
                "Summarize key modules, class and function distribution, and entry point bindings."
            ),
            expected_output="Architectural summary of code modules, classes, and internal function organization.",
            agent=agent
        )

    @staticmethod
    def dependency_task(agent: Agent, dep_context: str) -> Task:
        return Task(
            description=(
                f"Analyze module dependency relationships and execution flow.\n"
                f"Dependency Data:\n{dep_context}\n"
                "Review the generated Mermaid flowchart, check for circular dependencies, and explain the system flow."
            ),
            expected_output="Explanation of module dependencies, architectural pattern, and verification of Mermaid flowchart.",
            agent=agent
        )

    @staticmethod
    def intelligence_task(agent: Agent, full_context: str) -> Task:
        return Task(
            description=(
                f"Synthesize all domain findings into an authoritative technical review.\n"
                f"Comprehensive Context:\n{full_context}\n"
                "Assess repository health, maintainability, technical debt, security and testing risks. "
                "Provide prioritized, concrete recommendations (HIGH, MEDIUM, LOW) and infer local execution steps."
            ),
            expected_output="Senior engineering evaluation with health status, risks, technical debt, and prioritized recommendations.",
            agent=agent
        )

    @staticmethod
    def report_task(agent: Agent, summary_context: str) -> Task:
        return Task(
            description=(
                f"Review the finalized synthesis and ensure ready for publication in Markdown and XHTML.\n"
                f"Summary Data:\n{summary_context}\n"
                "Ensure crisp headings, accurate metrics, clean formatting, and no hallucinated information."
            ),
            expected_output="Final publication readiness confirmation for report generation.",
            agent=agent
        )
