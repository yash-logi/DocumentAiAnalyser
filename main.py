"""CLI and application entry point for the Agentic GitHub Repository Analyzer."""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from config.settings import settings
from crew.crew import RepositoryAnalyzerOrchestrator
from tools.github_client import parse_github_url


def configure_logging(level: str = "INFO"):
    """Configure structured logging format."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def run_cli():
    parser = argparse.ArgumentParser(
        description="Agentic GitHub Repository Analyzer: Autonomous Multi-Agent Codebase Inspection & Reporting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --repo https://github.com/pallets/flask
  python main.py --repo owner/repo --output ./custom_reports
  python main.py --repo https://github.com/owner/repo --no-llm
  python main.py --serve --port 8000
  python main.py --mock
        """
    )
    parser.add_argument("--repo", "-r", type=str, help="Public GitHub repository URL (e.g. https://github.com/owner/repo)")
    parser.add_argument("--output", "-o", type=str, default="reports", help="Directory where reports are saved (default: reports)")
    parser.add_argument("--no-llm", action="store_true", help="Run in deterministic mode without invoking LLM API")
    parser.add_argument("--serve", action="store_true", help="Launch FastAPI REST server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for API server (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port for API server (default: 8000)")
    parser.add_argument("--mock", action="store_true", help="Run demonstration analysis on simulated repository data")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log verbosity")

    args = parser.parse_args()

    configure_logging(args.log_level)
    settings.output_dir = Path(args.output)

    # 1. Server mode
    if args.serve:
        import uvicorn
        print(f"[INFO] Starting FastAPI server on http://{args.host}:{args.port}")
        uvicorn.run("api.main:app", host=args.host, port=args.port, reload=False)
        return

    # 2. Mock mode
    if args.mock or (not args.repo and len(sys.argv) == 1):
        print("[INFO] Running demo mode with simulated repository data...")
        from tests.mock_data import create_mock_github_client
        mock_client = create_mock_github_client()
        orchestrator = RepositoryAnalyzerOrchestrator(github_client=mock_client, use_llm=False)
        report = orchestrator.analyze("https://github.com/example-org/agentic-analyzer-demo")
        print("\n" + "=" * 60)
        print("DEMO ANALYSIS COMPLETED SUCCESSFULLY!")
        print(f"Health Score: {report.intelligence.repository_health_score}/100 ({report.intelligence.health_status})")
        print(f"Markdown Report: {report.markdown_path}")
        print(f"XHTML Report:    {report.xhtml_path}")
        print(f"Mermaid Diagram: {report.diagram_path}")
        print("=" * 60)
        return

    # 3. Live Repository Analysis
    if not args.repo:
        parser.print_help()
        sys.exit(1)

    print(f"[INFO] Initializing analysis for repository: {args.repo}")
    orchestrator = RepositoryAnalyzerOrchestrator(use_llm=not args.no_llm)

    try:
        report = orchestrator.analyze(args.repo)
        print("\n" + "=" * 60)
        print("REPOSITORY ANALYSIS COMPLETE!")
        print(f"Target:          {report.repository_name}")
        print(f"Health:          {report.intelligence.health_status} ({report.intelligence.repository_health_score}/100)")
        print(f"Modules Scanned: {report.code_data.total_modules_analyzed}")
        print(f"Markdown Report: {report.markdown_path}")
        print(f"XHTML Report:    {report.xhtml_path}")
        print(f"Mermaid Diagram: {report.diagram_path}")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
