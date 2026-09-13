"""FastAPI REST API server for repository analysis."""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from crew.crew import RepositoryAnalyzerOrchestrator
from tools.github_client import GitHubAPIError, RepositoryNotFoundError, RateLimitExceededError

app = FastAPI(
    title="Agentic GitHub Repository Analyzer API",
    description="Multi-agent automated GitHub repository analysis engine powered by CrewAI and GitHub MCP/REST APIs.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    repository_url: str = Field(..., json_schema_extra={"example": "https://github.com/pallets/flask"})
    use_llm: bool = Field(default=True, description="Whether to employ LLM for agentic reasoning")


class AnalyzeResponse(BaseModel):
    status: str
    repository: str
    health_score: int
    health_status: str
    report_path: Optional[str] = None
    xhtml_path: Optional[str] = None
    diagram_path: Optional[str] = None
    executive_summary: str


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_repository(request: AnalyzeRequest):
    """Analyze a public GitHub repository and generate reports."""
    orchestrator = RepositoryAnalyzerOrchestrator(use_llm=request.use_llm)
    try:
        report = orchestrator.analyze(request.repository_url)
        return AnalyzeResponse(
            status="completed",
            repository=report.repository_name,
            health_score=report.intelligence.repository_health_score,
            health_status=report.intelligence.health_status,
            report_path=report.markdown_path,
            xhtml_path=report.xhtml_path,
            diagram_path=report.diagram_path,
            executive_summary=report.intelligence.executive_summary
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RepositoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RateLimitExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except GitHubAPIError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")


@app.get("/reports/{filename}")
def get_report_file(filename: str):
    """Serve generated report files."""
    for sub in ["markdown", "xhtml", "diagrams"]:
        target = settings.output_dir / sub / filename
        if target.exists():
            media_type = "text/html" if filename.endswith((".html", ".xhtml")) else "text/plain"
            return FileResponse(str(target), media_type=media_type)
    raise HTTPException(status_code=404, detail=f"Report file '{filename}' not found.")
