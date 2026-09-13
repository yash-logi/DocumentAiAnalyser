"""Unit tests for GitHub API client and error handling."""

from unittest.mock import patch, MagicMock
import httpx
import pytest
from tools.github_client import (
    GitHubClient, RepositoryNotFoundError, RateLimitExceededError, AuthenticationError
)


def test_github_client_headers():
    client = GitHubClient(token="secret-token-123")
    assert "Bearer secret-token-123" in client._headers.get("Authorization", "")
    assert client._headers.get("Accept") == "application/vnd.github.v3+json"


@patch("httpx.Client.get")
def test_github_client_404_not_found(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.json.return_value = {"message": "Not Found"}
    mock_get.return_value = mock_resp

    client = GitHubClient()
    with pytest.raises(RepositoryNotFoundError):
        client.get_repository("nonexistent", "repo")


@patch("httpx.Client.get")
def test_github_client_rate_limit(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.text = "API rate limit exceeded for IP"
    mock_get.return_value = mock_resp

    client = GitHubClient()
    with pytest.raises(RateLimitExceededError):
        client.get_repository("owner", "repo")


@patch("httpx.Client.get")
def test_github_client_filters_prs_from_issues(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {}
    mock_resp.json.return_value = [
        {"number": 1, "title": "Real issue"},
        {"number": 2, "title": "PR labeled as issue", "pull_request": {"url": "..."}}
    ]
    mock_get.return_value = mock_resp

    client = GitHubClient()
    issues = client.get_issues("owner", "repo")
    assert len(issues) == 1
    assert issues[0]["title"] == "Real issue"
