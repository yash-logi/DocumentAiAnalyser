"""Unit tests for report generator."""

from pathlib import Path
import tempfile
from tools.report_generator import ReportGenerator
from tests.mock_data import create_mock_github_client
from crew.crew import RepositoryAnalyzerOrchestrator


def test_report_generator():
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_client = create_mock_github_client()
        orchestrator = RepositoryAnalyzerOrchestrator(github_client=mock_client, use_llm=False)
        report = orchestrator.analyze("https://github.com/example-org/agentic-analyzer-demo")

        gen = ReportGenerator(output_dir=Path(tmpdir))
        md_p, xhtml_p, diag_p = gen.generate_all(report)

        assert md_p.exists()
        assert xhtml_p.exists()
        assert diag_p.exists()

        md_text = md_p.read_text(encoding="utf-8")
        assert "agentic-analyzer-demo" in md_text
        assert "flowchart TD" in md_text

        xhtml_text = xhtml_p.read_text(encoding="utf-8")
        assert "<!DOCTYPE html" in xhtml_text
        assert "mermaid.min.js" in xhtml_text
