"""Unified GitHub API Client with robust error handling and rate-limit tracking."""

import re
import base64
import logging
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
import httpx

from config.settings import settings
from models.repository import RepositoryRef

logger = logging.getLogger("agentic_github_analyzer.github_client")


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Any] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class RepositoryNotFoundError(GitHubAPIError):
    """Raised when the repository does not exist or is private without authentication."""
    pass


class RateLimitExceededError(GitHubAPIError):
    """Raised when GitHub API rate limits are hit."""
    pass


class AuthenticationError(GitHubAPIError):
    """Raised when an invalid GitHub token is provided."""
    pass


def parse_github_url(url: str) -> RepositoryRef:
    """
    Parse and validate a GitHub repository URL into an owner and repo.
    Supports https://github.com/owner/repo, git@github.com:owner/repo.git, and owner/repo.
    """
    if not url or not isinstance(url, str):
        raise ValueError("Repository URL must be a non-empty string.")

    cleaned = url.strip()

    # Pattern 1: owner/repo directly
    simple_match = re.match(r"^([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)$", cleaned)
    if simple_match:
        owner, repo = simple_match.groups()
        return RepositoryRef(owner=owner, repo=repo.removesuffix(".git"), original_url=url)

    # Pattern 2: SSH format git@github.com:owner/repo.git
    ssh_match = re.match(r"^git@github\.com:([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?$", cleaned)
    if ssh_match:
        owner, repo = ssh_match.groups()
        return RepositoryRef(owner=owner, repo=repo, original_url=url)

    # Pattern 3: Standard HTTPS URL
    parsed = urlparse(cleaned)
    if not parsed.netloc:
        # Check if missing protocol e.g. github.com/owner/repo
        if cleaned.startswith("github.com/"):
            parsed = urlparse("https://" + cleaned)
        else:
            raise ValueError(f"Invalid GitHub repository URL: '{url}'. Expected format 'https://github.com/owner/repo'")

    if parsed.netloc.lower() not in ("github.com", "www.github.com"):
        raise ValueError(f"Unsupported host '{parsed.netloc}'. Only 'github.com' is supported.")

    path_parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(path_parts) < 2:
        raise ValueError(f"Invalid repository path in URL: '{url}'. Expected '/owner/repo'.")

    owner = path_parts[0]
    repo = path_parts[1].removesuffix(".git")

    if not owner or not repo:
        raise ValueError(f"Could not extract valid owner and repository from '{url}'.")

    return RepositoryRef(owner=owner, repo=repo, original_url=url)


class GitHubClient:
    """Client for interacting with GitHub REST API."""

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None, timeout: float = 25.0):
        self.token = token or settings.github_token
        self.base_url = (base_url or settings.github_api_base).rstrip("/")
        self.timeout = timeout
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "agentic-github-analyzer/1.0"
        }
        if self.token:
            self._headers["Authorization"] = f"Bearer {self.token}"

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Internal HTTP GET with error and rate limit handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            with httpx.Client(headers=self._headers, timeout=self.timeout, follow_redirects=True) as client:
                response = client.get(url, params=params)

                # Track rate limits
                remaining = response.headers.get("x-ratelimit-remaining")
                if remaining is not None and int(remaining) < 5:
                    logger.warning(f"[WARNING] GitHub rate limit low! Remaining calls: {remaining}")

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    raise RepositoryNotFoundError(
                        f"Resource not found at {endpoint}. Verify repository existence and access permissions.",
                        status_code=404
                    )
                elif response.status_code in (401, 403) and "rate limit" in response.text.lower():
                    raise RateLimitExceededError(
                        "GitHub API rate limit exceeded. Set GITHUB_TOKEN in .env for higher rate limits (5,000/hr).",
                        status_code=response.status_code
                    )
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid or expired GitHub token.", status_code=401)
                else:
                    response.raise_for_status()
                    return response.json()
        except httpx.RequestError as exc:
            logger.error(f"[ERROR] Network error contacting GitHub API: {exc}")
            raise GitHubAPIError(f"Network error contacting GitHub API: {exc}") from exc

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch general repository metadata."""
        return self._get(f"repos/{owner}/{repo}")

    def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Fetch language byte breakdown."""
        try:
            return self._get(f"repos/{owner}/{repo}/languages")
        except GitHubAPIError as e:
            logger.warning(f"[WARNING] Failed to fetch languages: {e}")
            return {}

    def get_git_tree(self, owner: str, repo: str, branch: str = "main") -> List[Dict[str, Any]]:
        """
        Fetch the complete recursive file tree for the repository in a single API call.
        Falls back to 'master' if 'main' returns 404.
        """
        for b in [branch, "main", "master"]:
            try:
                data = self._get(f"repos/{owner}/{repo}/git/trees/{b}", params={"recursive": "1"})
                if isinstance(data, dict) and "tree" in data:
                    return data["tree"]
            except RepositoryNotFoundError:
                continue
            except Exception as e:
                logger.warning(f"[WARNING] Could not fetch tree on branch '{b}': {e}")
                break
        return []

    def get_issues(self, owner: str, repo: str, state: str = "all", per_page: int = 50) -> List[Dict[str, Any]]:
        """Fetch issues (excluding pull requests)."""
        params = {"state": state, "per_page": min(per_page, 100), "sort": "updated", "direction": "desc"}
        raw_items = self._get(f"repos/{owner}/{repo}/issues", params=params)
        if not isinstance(raw_items, list):
            return []
        # Filter out pull requests as GitHub returns PRs in /issues endpoint
        return [item for item in raw_items if "pull_request" not in item]

    def get_pull_requests(self, owner: str, repo: str, state: str = "all", per_page: int = 30) -> List[Dict[str, Any]]:
        """Fetch pull requests."""
        params = {"state": state, "per_page": min(per_page, 100), "sort": "updated", "direction": "desc"}
        raw_prs = self._get(f"repos/{owner}/{repo}/pulls", params=params)
        return raw_prs if isinstance(raw_prs, list) else []

    def get_branches(self, owner: str, repo: str, per_page: int = 30) -> List[Dict[str, Any]]:
        """Fetch repository branches."""
        params = {"per_page": min(per_page, 100)}
        branches = self._get(f"repos/{owner}/{repo}/branches", params=params)
        return branches if isinstance(branches, list) else []

    def get_commits(self, owner: str, repo: str, per_page: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent commit history."""
        params = {"per_page": min(per_page, 100)}
        commits = self._get(f"repos/{owner}/{repo}/commits", params=params)
        return commits if isinstance(commits, list) else []

    def get_file_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> Optional[str]:
        """Fetch decoded content of a repository file."""
        params = {"ref": ref} if ref else None
        try:
            data = self._get(f"repos/{owner}/{repo}/contents/{path.lstrip('/')}", params=params)
            if isinstance(data, dict) and data.get("encoding") == "base64" and data.get("content"):
                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            elif isinstance(data, dict) and "content" in data:
                return data["content"]
        except Exception as e:
            logger.debug(f"[DEBUG] Could not fetch file {path}: {e}")
            return None
        return None
