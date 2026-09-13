"""Tests for FastAPI REST API endpoints."""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from api.main import app
from tests.mock_data import create_mock_github_client


def test_api_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("crew.crew.GitHubClient")
def test_api_analyze_endpoint(mock_gh_cls):
    mock_gh_cls.return_value = create_mock_github_client()

    client = TestClient(app)
    payload = {
        "repository_url": "https://github.com/example-org/agentic-analyzer-demo",
        "use_llm": False
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["repository"] == "example-org/agentic-analyzer-demo"
    assert "report_path" in data
    assert "xhtml_path" in data
