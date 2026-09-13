"""Report generator compiling Markdown, XHTML, and Mermaid diagram artifacts."""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config.settings import settings
from models.analysis import CompleteAnalysisReport

logger = logging.getLogger("agentic_github_analyzer.report_generator")


class ReportGenerator:
    """Renders structured analysis results into Markdown, XHTML, and Mermaid diagrams."""

    def __init__(self, templates_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or (Path(__file__).parent.parent / "templates")
        self.output_dir = output_dir or settings.output_dir
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xhtml", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate_all(self, report: CompleteAnalysisReport) -> Tuple[Path, Path, Path]:
        """Generate markdown, xhtml, and mermaid diagram files."""
        safe_name = report.overview.metadata.full_name.replace("/", "_")
        md_dir = self.output_dir / "markdown"
        xhtml_dir = self.output_dir / "xhtml"
        diagram_dir = self.output_dir / "diagrams"

        for d in (md_dir, xhtml_dir, diagram_dir):
            d.mkdir(parents=True, exist_ok=True)

        # 1. Render Markdown
        logger.info(f"[INFO] Rendering Markdown report for {report.repository_name}")
        md_template = self.env.get_template("report_template.md")
        md_content = md_template.render(report=report)
        md_path = md_dir / f"{safe_name}_report.md"
        md_canonical = md_dir / "report.md"
        md_path.write_text(md_content, encoding="utf-8")
        md_canonical.write_text(md_content, encoding="utf-8")

        # 2. Render XHTML
        logger.info(f"[INFO] Rendering XHTML report for {report.repository_name}")
        xhtml_template = self.env.get_template("report_template.xhtml")
        xhtml_content = xhtml_template.render(report=report)
        xhtml_path = xhtml_dir / f"{safe_name}_report.xhtml"
        xhtml_canonical = xhtml_dir / "report.xhtml"
        xhtml_path.write_text(xhtml_content, encoding="utf-8")
        xhtml_canonical.write_text(xhtml_content, encoding="utf-8")

        # 3. Save Mermaid diagram
        logger.info(f"[INFO] Saving Mermaid diagram for {report.repository_name}")
        diagram_path = diagram_dir / f"{safe_name}_diagram.mmd"
        diagram_canonical = diagram_dir / "dependency_graph.mmd"
        diagram_path.write_text(report.dependency_data.mermaid_diagram, encoding="utf-8")
        diagram_canonical.write_text(report.dependency_data.mermaid_diagram, encoding="utf-8")

        report.markdown_path = str(md_canonical.resolve())
        report.xhtml_path = str(xhtml_canonical.resolve())
        report.diagram_path = str(diagram_canonical.resolve())

        return md_canonical, xhtml_canonical, diagram_canonical
