"""Full integration test for complete multi-agent repository analyzer pipeline."""

from pathlib import Path
import tempfile
from crew.crew import RepositoryAnalyzerOrchestrator
from tests.mock_data import create_mock_github_client


def test_full_pipeline_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_client = create_mock_github_client()
        orchestrator = RepositoryAnalyzerOrchestrator(github_client=mock_client, use_llm=False)
        orchestrator.report_generator.output_dir = Path(tmpdir)

        report = orchestrator.analyze("https://github.com/example-org/agentic-analyzer-demo")

        # Verify all agent outputs
        # 1. Repository Discovery
        assert report.overview.metadata.full_name == "example-org/agentic-analyzer-demo"
        assert "Python" in report.overview.structure.languages
        assert report.overview.structure.docker_present is True
        assert report.overview.structure.ci_cd_present is True

        # 2. Issue Analysis
        assert report.issue_data.total_issues_analyzed == 4
        assert report.issue_data.open_issues == 2
        assert len(report.issue_data.major_bugs) >= 1

        # 3. Pull Request Analysis
        assert report.pr_data.total_prs_analyzed == 2
        assert report.pr_data.open_prs == 1
        assert report.pr_data.merged_prs == 1

        # 4. Git History Analysis
        assert report.git_data.total_branches == 4
        assert len(report.git_data.recent_commits) >= 1

        # 5. Code Structure Analysis
        assert report.code_data.total_modules_analyzed >= 4
        assert report.code_data.classes_count >= 1

        # 6. Dependency Analysis
        assert len(report.dependency_data.nodes) >= 4
        assert "flowchart TD" in report.dependency_data.mermaid_diagram

        # 7. Intelligence Synthesis
        assert 0 <= report.intelligence.repository_health_score <= 100
        assert report.intelligence.health_status in ("Excellent", "Good", "Fair", "Needs Attention", "Critical")

        # 8. How to Run
        assert len(report.how_to_run.installation_steps) >= 2
        assert "requirements.txt" in report.how_to_run.detected_manifests

        # Report files verification
        assert report.markdown_path is not None
        assert report.xhtml_path is not None
        assert report.diagram_path is not None
