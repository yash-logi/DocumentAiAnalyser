"""CrewAI Orchestrator coordinating all 8 agents and deterministic tools."""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path

from config.settings import settings
from models import (
    RepositoryRef, RepositoryOverview, IssueItem, IssueAnalysisData,
    PullRequestItem, PRAnalysisData, BranchItem, CommitItem, BranchCommitData,
    CodeStructureData, DependencyGraphData, ActionRecommendation,
    IntelligenceSummary, HowToRunPlan, CompleteAnalysisReport
)
from tools import (
    GitHubClient, GitHubMCPBridge, RepositoryScanner, CodeParser,
    DependencyAnalyzer, ReportGenerator, parse_github_url
)
from crew.agents import RepositoryCrewAgents, get_llm_instance
from crew.tasks import RepositoryCrewTasks
from crewai import Crew, Process

logger = logging.getLogger("agentic_github_analyzer.orchestrator")


class RepositoryAnalyzerOrchestrator:
    """Master orchestrator for multi-agent repository inspection and report generation."""

    def __init__(self, github_client: Optional[GitHubClient] = None, use_llm: bool = True):
        self.client = github_client or GitHubClient()
        self.mcp = GitHubMCPBridge(self.client)
        self.scanner = RepositoryScanner(self.client)
        self.report_generator = ReportGenerator()
        self.use_llm = use_llm
        self.llm = get_llm_instance() if use_llm else None

    def analyze(self, repository_url: str) -> CompleteAnalysisReport:
        """Execute end-to-end multi-agent analysis."""
        start_time = time.time()
        logger.info(f"[INFO] Starting repository analysis for: {repository_url}")

        # 1. Parse and validate URL
        repo_ref = parse_github_url(repository_url)
        logger.info(f"[INFO] Repository validated: {repo_ref.full_name}")

        # 2. Agent 1 — Repository Discovery
        logger.info(f"[INFO] Running Agent 1 (Repository Explorer) for {repo_ref.full_name}")
        overview = self.scanner.scan(repo_ref)
        logger.info(f"[INFO] Discovered {len(overview.structure.languages)} languages, {len(overview.structure.config_files)} configs, {overview.structure.total_files_scanned} files.")

        # 3. Agent 2 — Issue Analysis
        logger.info("[INFO] Running Agent 2 (Issue Analyst)...")
        raw_issues = self.mcp.list_issues(repo_ref.owner, repo_ref.repo, state="all", per_page=settings.max_issues_to_fetch).get("issues", [])
        issue_data = self._process_issues(raw_issues)

        # 4. Agent 3 — Pull Request Analysis
        logger.info("[INFO] Running Agent 3 (Pull Request Analyst)...")
        raw_prs = self.mcp.list_pull_requests(repo_ref.owner, repo_ref.repo, state="all", per_page=settings.max_prs_to_fetch).get("pull_requests", [])
        pr_data = self._process_pull_requests(raw_prs)

        # 5. Agent 4 — Git History Analysis
        logger.info("[INFO] Running Agent 4 (Git History Analyst)...")
        raw_branches = self.mcp.list_branches(repo_ref.owner, repo_ref.repo, per_page=30).get("branches", [])
        raw_commits = self.mcp.list_commits(repo_ref.owner, repo_ref.repo, per_page=settings.max_commits_to_fetch).get("commits", [])
        git_data = self._process_git_history(raw_branches, raw_commits, overview.metadata.default_branch)

        # 6. Agent 5 — Code Structure Analysis
        logger.info("[INFO] Running Agent 5 (Codebase Architect)...")
        code_data = self._analyze_code_structure(repo_ref, overview)

        # 7. Agent 6 — Dependency & Workflow Analysis
        logger.info("[INFO] Running Agent 6 (Software Architecture Analyst)...")
        dependency_data = DependencyAnalyzer.analyze(code_data, overview)

        # 8. Agent 7 — Repository Intelligence & Synthesis
        logger.info("[INFO] Running Agent 7 (Repository Intelligence Agent)...")
        intelligence = self._synthesize_intelligence(overview, issue_data, pr_data, git_data, code_data, dependency_data)

        # 9. How-To-Run Planning
        how_to_run = self._infer_how_to_run(overview, code_data)

        # 10. Agent 8 — Report Generation
        logger.info("[INFO] Running Agent 8 (Technical Report Writer)...")
        duration = time.time() - start_time
        report = CompleteAnalysisReport(
            repository_name=repo_ref.full_name,
            overview=overview,
            issue_data=issue_data,
            pr_data=pr_data,
            git_data=git_data,
            code_data=code_data,
            dependency_data=dependency_data,
            intelligence=intelligence,
            how_to_run=how_to_run,
            duration_seconds=duration
        )

        md_path, xhtml_path, diagram_path = self.report_generator.generate_all(report)
        logger.info(f"[INFO] Analysis completed in {duration:.2f}s!")
        logger.info(f"[INFO] Markdown Report: {md_path}")
        logger.info(f"[INFO] XHTML Report: {xhtml_path}")
        logger.info(f"[INFO] Diagram: {diagram_path}")

        return report

    def _process_issues(self, raw_issues: List[Dict[str, Any]]) -> IssueAnalysisData:
        """Process and categorize issues."""
        open_count = 0
        closed_count = 0
        bugs = []
        features = []
        recurring = []
        unresolved = []
        priority = {"high": 0, "medium": 0, "low": 0}

        now = datetime.now(timezone.utc)

        for issue in raw_issues:
            state = issue.get("state", "open")
            title = issue.get("title", "")
            labels = [lbl.get("name", "").lower() for lbl in issue.get("labels", []) if isinstance(lbl, dict)]
            created_at_str = issue.get("created_at")

            if state == "open":
                open_count += 1
                unresolved.append(f"#{issue.get('number')}: {title}")
            else:
                closed_count += 1

            # Bug identification
            if "bug" in labels or any(kw in title.lower() for kw in ("bug", "crash", "error", "fail", "broken", "leak")):
                bugs.append(f"#{issue.get('number')}: {title}")

            # Feature request identification
            if any(kw in labels for kw in ("enhancement", "feature", "proposal")) or "feature" in title.lower():
                features.append(f"#{issue.get('number')}: {title}")

            # Priority categorization
            if any(p in labels for p in ("p0", "priority: high", "critical", "urgent", "high")):
                priority["high"] += 1
            elif any(p in labels for p in ("p1", "priority: medium", "medium")):
                priority["medium"] += 1
            else:
                priority["low"] += 1

        # Check for recurring keywords
        title_corpus = " ".join([i.get("title", "").lower() for i in raw_issues])
        for theme in ["auth", "login", "timeout", "memory", "race condition", "windows", "permission", "cors", "database", "docker"]:
            count = title_corpus.count(theme)
            if count >= 2:
                recurring.append(f"Recurring theme detected: '{theme}' referenced {count} times across issues")

        total = open_count + closed_count
        trend = "Stable"
        if total > 0:
            open_ratio = open_count / total
            if open_ratio > 0.6:
                trend = "High open backlog; potential triage backlog"
            elif open_ratio < 0.2:
                trend = "Active and responsive issue triage"

        return IssueAnalysisData(
            total_issues_analyzed=total,
            open_issues=open_count,
            closed_issues=closed_count,
            major_bugs=bugs[:6],
            feature_requests=features[:6],
            recurring_problems=recurring[:5],
            unresolved_issues=unresolved[:6],
            priority_breakdown=priority,
            recommended_actions=[
                "Triage high-priority bug reports." if priority["high"] > 0 else "Maintain current issue review cadence.",
                "Review stale open issues with no activity." if open_count > 10 else "Issue queue is healthy."
            ],
            trends=trend
        )

    def _process_pull_requests(self, raw_prs: List[Dict[str, Any]]) -> PRAnalysisData:
        """Process and evaluate pull requests."""
        open_count = 0
        merged_count = 0
        closed_unmerged = 0
        important_prs = []
        risky_changes = []
        file_frequency: Dict[str, int] = {}
        stale_prs = []

        now = datetime.now(timezone.utc)

        for pr in raw_prs:
            state = pr.get("state", "open")
            is_merged = bool(pr.get("merged_at"))
            title = pr.get("title", "")
            pr_num = pr.get("number")
            updated_at_str = pr.get("updated_at")

            if is_merged:
                merged_count += 1
            elif state == "open":
                open_count += 1
                if updated_at_str:
                    try:
                        up_dt = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                        if (now - up_dt).days > 30:
                            stale_prs.append(f"PR #{pr_num} ('{title}') inactive for {(now - up_dt).days} days")
                    except Exception:
                        pass
            else:
                closed_unmerged += 1

            # Important / large PR check
            labels = [lbl.get("name", "").lower() for lbl in pr.get("labels", []) if isinstance(lbl, dict)]
            if any(l in labels for l in ("breaking-change", "major", "security", "architecture")) or any(k in title.lower() for k in ("refactor", "breaking", "rewrite")):
                important_prs.append(f"PR #{pr_num}: {title}")

        trend = "Healthy pull request velocity"
        if len(stale_prs) > 3:
            trend = "Accumulating stale PRs awaiting review or updates"

        return PRAnalysisData(
            total_prs_analyzed=len(raw_prs),
            open_prs=open_count,
            merged_prs=merged_count,
            closed_unmerged_prs=closed_unmerged,
            important_prs=important_prs[:5],
            risky_changes=risky_changes[:5],
            frequently_changed_files=[],
            stale_prs=stale_prs[:5],
            development_trends=trend
        )

    def _process_git_history(self, raw_branches: List[Dict[str, Any]], raw_commits: List[Dict[str, Any]], default_branch: str) -> BranchCommitData:
        """Process Git branch and commit telemetry."""
        active_branches = []
        stale_branches = []
        contributors: Dict[str, int] = {}

        for b in raw_branches:
            name = b.get("name", "")
            if name == default_branch or any(k in name.lower() for k in ("main", "master", "dev", "develop")):
                active_branches.append(name)
            else:
                stale_branches.append(name)

        recent_commits_summary = []
        for c in raw_commits[:10]:
            commit_obj = c.get("commit", {})
            author_info = commit_obj.get("author", {}) or {}
            author_name = author_info.get("name", "Unknown")
            message = commit_obj.get("message", "").split("\n")[0]
            contributors[author_name] = contributors.get(author_name, 0) + 1
            recent_commits_summary.append(f"{message[:60]} (by {author_name})")

        top_contribs = sorted(contributors.items(), key=lambda x: x[1], reverse=True)
        top_contrib_strings = [f"{name} ({count} commits in sample)" for name, count in top_contribs[:5]]

        velocity = "Active continuous commits" if len(raw_commits) >= 20 else "Moderate commit activity"

        return BranchCommitData(
            total_branches=len(raw_branches),
            active_branches=active_branches[:8],
            stale_branches=stale_branches[:8],
            recent_commits=recent_commits_summary,
            commit_frequency_summary=f"{len(raw_commits)} commits retrieved in recent history",
            frequently_modified_files=[],
            top_contributors=top_contrib_strings,
            velocity_trends=velocity
        )

    def _analyze_code_structure(self, repo_ref: RepositoryRef, overview: RepositoryOverview) -> CodeStructureData:
        """Fetch candidate source files and perform deterministic AST parsing."""
        tree = self.client.get_git_tree(repo_ref.owner, repo_ref.repo, branch=overview.metadata.default_branch)
        code_extensions = (".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs")

        candidate_files = []
        # Prioritize entry points and core directories
        for item in tree:
            if item.get("type") == "blob":
                path = item.get("path", "")
                if path.endswith(code_extensions):
                    score = 0
                    if path in overview.structure.entry_points:
                        score += 100
                    if any(path.startswith(d + "/") for d in ("src", "app", "lib", "core", "api", "services")):
                        score += 50
                    if not any(test_dir in path for test_dir in ("test", "tests", "fixtures", "node_modules", "vendor")):
                        score += 20
                    candidate_files.append((score, path))

        # Sort by score and select up to max_files_for_ast
        candidate_files.sort(key=lambda x: x[0], reverse=True)
        selected_paths = [p for _, p in candidate_files[:settings.max_files_for_ast]]

        file_map = {}
        for path in selected_paths:
            content = self.client.get_file_content(repo_ref.owner, repo_ref.repo, path, ref=overview.metadata.default_branch)
            if content:
                file_map[path] = content

        if not file_map:
            logger.info("[INFO] No code files fetched or repository is non-code.")
            return CodeStructureData()

        return CodeParser.analyze_repository_code(file_map)

    def _synthesize_intelligence(
        self,
        overview: RepositoryOverview,
        issue_data: IssueAnalysisData,
        pr_data: PRAnalysisData,
        git_data: BranchCommitData,
        code_data: CodeStructureData,
        dependency_data: DependencyGraphData
    ) -> IntelligenceSummary:
        """Synthesize overall health, risk, and prioritized actions."""
        # Calculate dynamic health score
        score = 70
        risks = []
        technical_debt = []
        recs_high = []
        recs_medium = []
        recs_low = []

        # Tests evaluation
        has_tests = any("test" in d.lower() for d in overview.structure.important_directories) or any("test" in f.lower() for f in code_data.modules)
        if has_tests:
            score += 10
            testing_sit = "Automated tests detected in repository."
        else:
            score -= 10
            testing_sit = "No explicit test directory or automated test suite detected."
            technical_debt.append("Absence of automated unit/integration tests.")
            recs_high.append(ActionRecommendation(
                priority="HIGH",
                category="Testing",
                description="Introduce automated test suite (e.g., pytest, jest, go test).",
                rationale="Unverified pull requests risk introducing regressions into production."
            ))

        # CI/CD evaluation
        if overview.structure.ci_cd_present:
            score += 10
        else:
            score -= 5
            risks.append("No CI/CD automation workflow detected.")
            recs_medium.append(ActionRecommendation(
                priority="MEDIUM",
                category="CI/CD",
                description="Configure automated GitHub Actions for build and test validation.",
                rationale="Ensures continuous integration before code lands in main."
            ))

        # README evaluation
        if overview.structure.readme_present:
            score += 5
            doc_quality = "README documentation is present."
        else:
            score -= 15
            doc_quality = "Missing README file."
            risks.append("Project lacks basic onboarding or architectural documentation.")
            recs_high.append(ActionRecommendation(
                priority="HIGH",
                category="Documentation",
                description="Add comprehensive README.md with setup and usage instructions.",
                rationale="Critical for developer onboarding and project adoption."
            ))

        # License evaluation
        if overview.metadata.license_name:
            score += 5
        else:
            risks.append("No open-source license detected.")
            recs_low.append(ActionRecommendation(
                priority="LOW",
                category="Legal / Compliance",
                description="Declare a software license (e.g., MIT, Apache-2.0).",
                rationale="Clarifies copyright and reuse terms for contributors."
            ))

        # Circular dependencies
        if dependency_data.circular_dependencies:
            score -= 10
            for cycle in dependency_data.circular_dependencies:
                technical_debt.append(f"Circular dependency: {cycle}")
            recs_high.append(ActionRecommendation(
                priority="HIGH",
                category="Architecture",
                description="Refactor circular dependencies between internal modules.",
                rationale="Circular couplings impede testing, increase tight coupling, and cause runtime import errors."
            ))

        # Stale PRs
        if len(pr_data.stale_prs) > 2:
            score -= 5
            recs_medium.append(ActionRecommendation(
                priority="MEDIUM",
                category="Maintenance",
                description=f"Address {len(pr_data.stale_prs)} stale pull requests awaiting triage.",
                rationale="Prevents merge conflicts and improves contributor retention."
            ))

        # Bound score
        score = max(20, min(100, score))
        health_status = "Excellent" if score >= 85 else ("Good" if score >= 70 else ("Fair" if score >= 50 else "Critical"))

        exec_summary = (
            f"The repository '{overview.metadata.full_name}' is currently rated as **{health_status}** ({score}/100). "
            f"Primary languages include {', '.join(overview.structure.languages[:3]) if overview.structure.languages else 'Unspecified'}. "
            f"The codebase contains {code_data.total_modules_analyzed} analyzed source modules following a {dependency_data.architectural_pattern} pattern. "
            f"Activity indicators show {issue_data.open_issues} open issues and {pr_data.open_prs} open PRs."
        )

        return IntelligenceSummary(
            repository_health_score=score,
            health_status=health_status,
            executive_summary=exec_summary,
            development_activity_summary=f"Velocity is {git_data.velocity_trends.lower()} with {pr_data.development_trends.lower()}.",
            issue_trends=issue_data.trends,
            pr_trends=pr_data.development_trends,
            branch_activity_summary=f"{len(git_data.active_branches)} active branches vs {len(git_data.stale_branches)} stale branches.",
            code_architecture_evaluation=f"Identified {code_data.classes_count} classes and {code_data.functions_count} functions across {code_data.total_modules_analyzed} modules.",
            potential_technical_debt=technical_debt,
            potential_risks=risks,
            documentation_quality=doc_quality,
            testing_situation=testing_sit,
            dependency_concerns=dependency_data.circular_dependencies,
            maintainability_score="High" if score >= 75 else "Moderate",
            recommendations_high=recs_high,
            recommendations_medium=recs_medium,
            recommendations_low=recs_low
        )

    def _infer_how_to_run(self, overview: RepositoryOverview, code_data: CodeStructureData) -> HowToRunPlan:
        """Analyze repository manifest files and deduce setup and execution instructions."""
        prereqs = ["git (v2.x or higher)"]
        install = [f"git clone {overview.metadata.homepage or 'https://github.com/' + overview.metadata.full_name}", f"cd {overview.metadata.name}"]
        config = []
        exec_steps = []
        manifests = overview.structure.manifest_files

        primary_lang = overview.structure.languages[0] if overview.structure.languages else ""

        # Python
        if "requirements.txt" in manifests or "pyproject.toml" in manifests or primary_lang == "Python":
            prereqs.append("Python 3.10+ and pip")
            install.append("python -m venv .venv")
            install.append("# On Windows: .venv\\Scripts\\activate | On Linux/macOS: source .venv/bin/activate")
            if "requirements.txt" in manifests:
                install.append("pip install -r requirements.txt")
            elif "pyproject.toml" in manifests:
                install.append("pip install .")

            entry = overview.structure.entry_points[0] if overview.structure.entry_points else "main.py"
            exec_steps.append(f"python {entry}")

        # Node / JS / TS
        elif "package.json" in manifests or primary_lang in ("JavaScript", "TypeScript"):
            prereqs.append("Node.js 18+ and npm / pnpm / yarn")
            install.append("npm install")
            exec_steps.append("npm start # or npm run dev")

        # Docker
        if overview.structure.docker_present:
            prereqs.append("Docker Engine & Docker Compose")
            if "docker-compose.yml" in manifests or "docker-compose.yaml" in manifests:
                exec_steps.append("docker compose up --build")
            else:
                exec_steps.append(f"docker build -t {overview.metadata.name} . && docker run -p 8000:8000 {overview.metadata.name}")

        # Config files
        if ".env.example" in overview.structure.config_files:
            config.append("cp .env.example .env")
            config.append("# Edit .env with your specific API credentials")

        if not exec_steps:
            exec_steps.append("# Consult README for specific runtime commands")

        return HowToRunPlan(
            confidence_label="Likely execution procedure (Inferred from manifest indicators)",
            prerequisites=prereqs,
            installation_steps=install,
            configuration_steps=config if config else ["# No specific .env template detected"],
            execution_steps=exec_steps,
            detected_manifests=manifests,
            notes_and_warnings=["Review project README and security credentials before running in production."]
        )
