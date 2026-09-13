"""Mock repository dataset and mock GitHub client for unit and integration tests."""

from typing import Dict, Any, List, Optional
from unittest.mock import MagicMock
from tools.github_client import GitHubClient

MOCK_REPO_METADATA = {
    "name": "agentic-analyzer-demo",
    "full_name": "example-org/agentic-analyzer-demo",
    "description": "Demonstration repository showcasing multi-agent architectural analysis.",
    "default_branch": "main",
    "stargazers_count": 342,
    "forks_count": 48,
    "open_issues_count": 8,
    "subscribers_count": 22,
    "license": {"name": "MIT License", "spdx_id": "MIT"},
    "created_at": "2024-01-15T08:00:00Z",
    "updated_at": "2024-05-10T14:30:00Z",
    "pushed_at": "2024-05-10T14:25:00Z",
    "private": False,
    "archived": False,
    "fork": False,
    "homepage": "https://example.org/demo",
    "topics": ["ai", "agents", "github-api", "fastapi"]
}

MOCK_LANGUAGES = {
    "Python": 84500,
    "JavaScript": 12300,
    "Dockerfile": 850
}

MOCK_TREE = [
    {"path": "main.py", "type": "blob", "size": 1200},
    {"path": "config.py", "type": "blob", "size": 800},
    {"path": "services.py", "type": "blob", "size": 2400},
    {"path": "github_client.py", "type": "blob", "size": 3100},
    {"path": "analyzer.py", "type": "blob", "size": 2800},
    {"path": "models.py", "type": "blob", "size": 1500},
    {"path": "README.md", "type": "blob", "size": 3200},
    {"path": "requirements.txt", "type": "blob", "size": 420},
    {"path": "Dockerfile", "type": "blob", "size": 510},
    {"path": "docker-compose.yml", "type": "blob", "size": 450},
    {"path": ".env.example", "type": "blob", "size": 180},
    {"path": "src", "type": "tree"},
    {"path": "tests", "type": "tree"},
    {"path": "tests/test_main.py", "type": "blob", "size": 950},
    {"path": ".github", "type": "tree"},
    {"path": ".github/workflows/ci.yml", "type": "blob", "size": 650}
]

MOCK_FILE_CONTENTS = {
    "main.py": """
import config
import services
from analyzer import CodeAnalyzer

def start_application():
    cfg = config.load_config()
    services.initialize(cfg)
    analyzer = CodeAnalyzer()
    analyzer.run()

if __name__ == "__main__":
    start_application()
""",
    "config.py": """
import os

class AppConfig:
    def __init__(self):
        self.env = os.getenv("ENV", "production")
        self.token = os.getenv("API_KEY")

def load_config() -> AppConfig:
    return AppConfig()
""",
    "services.py": """
import config
import github_client

class RepositoryService:
    def __init__(self, cfg):
        self.client = github_client.GitHubClient()

def initialize(cfg):
    return RepositoryService(cfg)
""",
    "github_client.py": """
import config

class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.connected = True
    
    def fetch_data(self):
        return {"status": "ok"}
""",
    "analyzer.py": """
import models
import services

class CodeAnalyzer:
    def __init__(self):
        self.results = []
    
    def run(self):
        return models.AnalysisResult(status="passed")
""",
    "models.py": """
class AnalysisResult:
    def __init__(self, status: str):
        self.status = status
""",
    "requirements.txt": """fastapi>=0.111.0\nuvicorn>=0.30.0\nhttpx>=0.27.0\npydantic>=2.7.0\n""",
    ".env.example": """API_KEY=your_api_key_here\nENV=production\n"""
}

MOCK_ISSUES = [
    {
        "number": 101,
        "title": "Fix authentication timeout under high concurrency",
        "state": "open",
        "created_at": "2024-05-01T10:00:00Z",
        "updated_at": "2024-05-08T12:00:00Z",
        "labels": [{"name": "bug"}, {"name": "priority: high"}],
        "comments": 4,
        "author": {"login": "dev_alice"}
    },
    {
        "number": 102,
        "title": "Add support for custom webhook endpoints",
        "state": "open",
        "created_at": "2024-05-02T11:00:00Z",
        "updated_at": "2024-05-05T09:00:00Z",
        "labels": [{"name": "enhancement"}],
        "comments": 2,
        "author": {"login": "dev_bob"}
    },
    {
        "number": 95,
        "title": "Memory leak when scanning deep recursive directories",
        "state": "closed",
        "created_at": "2024-04-10T14:00:00Z",
        "updated_at": "2024-04-15T16:00:00Z",
        "closed_at": "2024-04-15T16:00:00Z",
        "labels": [{"name": "bug"}],
        "comments": 7,
        "author": {"login": "dev_carol"}
    },
    {
        "number": 90,
        "title": "Login fails when password contains special characters",
        "state": "closed",
        "created_at": "2024-04-01T09:00:00Z",
        "updated_at": "2024-04-03T11:00:00Z",
        "closed_at": "2024-04-03T11:00:00Z",
        "labels": [{"name": "bug"}, {"name": "auth"}],
        "comments": 3,
        "author": {"login": "dev_david"}
    }
]

MOCK_PULL_REQUESTS = [
    {
        "number": 120,
        "title": "Implement caching layer for GitHub API requests",
        "state": "open",
        "merged_at": None,
        "created_at": "2024-05-04T13:00:00Z",
        "updated_at": "2024-05-09T17:00:00Z",
        "author": {"login": "dev_alice"},
        "labels": [{"name": "performance"}]
    },
    {
        "number": 115,
        "title": "Refactor architecture and consolidate HTTP client",
        "state": "closed",
        "merged_at": "2024-05-02T16:00:00Z",
        "created_at": "2024-04-28T10:00:00Z",
        "updated_at": "2024-05-02T16:00:00Z",
        "author": {"login": "dev_bob"},
        "labels": [{"name": "refactor"}]
    }
]

MOCK_BRANCHES = [
    {"name": "main", "protected": True},
    {"name": "develop", "protected": False},
    {"name": "feature/caching", "protected": False},
    {"name": "stale-experiment-2023", "protected": False}
]

MOCK_COMMITS = [
    {
        "sha": "a1b2c3d4e5",
        "commit": {
            "message": "Add unit tests for AST parser",
            "author": {"name": "Alice Developer", "date": "2024-05-10T14:00:00Z"}
        }
    },
    {
        "sha": "f6g7h8i9j0",
        "commit": {
            "message": "Improve dependency graph resolution",
            "author": {"name": "Bob Architect", "date": "2024-05-09T11:00:00Z"}
        }
    },
    {
        "sha": "k1l2m3n4o5",
        "commit": {
            "message": "Update Dockerfile and CI configuration",
            "author": {"name": "Alice Developer", "date": "2024-05-07T09:30:00Z"}
        }
    }
]


def create_mock_github_client() -> GitHubClient:
    """Create a fully functional mock GitHub client for tests without network calls."""
    client = MagicMock(spec=GitHubClient)
    client.get_repository.return_value = MOCK_REPO_METADATA
    client.get_languages.return_value = MOCK_LANGUAGES
    client.get_git_tree.return_value = MOCK_TREE
    client.get_issues.return_value = MOCK_ISSUES
    client.get_pull_requests.return_value = MOCK_PULL_REQUESTS
    client.get_branches.return_value = MOCK_BRANCHES
    client.get_commits.return_value = MOCK_COMMITS
    client.get_file_content.side_effect = lambda owner, repo, path, ref=None: MOCK_FILE_CONTENTS.get(path)
    return client
