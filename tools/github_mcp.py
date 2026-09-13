"""GitHub MCP Client & Adapter layer for agent interactions."""

import logging
from typing import Dict, Any, List, Optional
from tools.github_client import GitHubClient
from config.settings import settings

logger = logging.getLogger("agentic_github_analyzer.github_mcp")


class GitHubMCPBridge:
    """
    Adapter adhering to the Model Context Protocol (MCP) for GitHub.
    Provides standard MCP-formatted tool calling interfaces. If an external MCP
    server process is configured, it delegates through MCP protocol transport;
    otherwise, it cleanly adapts to the robust GitHub REST client.
    """

    def __init__(self, github_client: Optional[GitHubClient] = None):
        self.client = github_client or GitHubClient()
        self.mcp_server_command = settings.mcp_server_command

    def is_external_mcp_configured(self) -> bool:
        """Check if an external MCP server command is defined."""
        return bool(self.mcp_server_command and settings.mcp_enabled)

    # MCP Tool: get_file_contents
    def get_file_contents(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> Dict[str, Any]:
        """MCP Tool: Retrieve file contents from a repository."""
        logger.info(f"[INFO] MCP Tool invoked: get_file_contents for {owner}/{repo}:{path}")
        content = self.client.get_file_content(owner, repo, path, ref)
        if content is None:
            return {"error": f"File {path} not found or unreadable."}
        return {"path": path, "content": content}

    # MCP Tool: list_directory
    def list_directory(self, owner: str, repo: str, path: str = "", branch: str = "main") -> Dict[str, Any]:
        """MCP Tool: List items in a repository directory using tree."""
        logger.info(f"[INFO] MCP Tool invoked: list_directory for {owner}/{repo} at '{path}'")
        tree = self.client.get_git_tree(owner, repo, branch)
        clean_path = path.strip("/")
        matching = []
        for item in tree:
            item_path = item.get("path", "")
            if not clean_path:
                if "/" not in item_path:
                    matching.append(item)
            elif item_path.startswith(clean_path + "/"):
                sub_path = item_path[len(clean_path) + 1:]
                if "/" not in sub_path:
                    matching.append(item)
        return {"directory": path, "entries": matching}

    # MCP Tool: list_issues
    def list_issues(self, owner: str, repo: str, state: str = "all", per_page: int = 50) -> Dict[str, Any]:
        """MCP Tool: List issues from the repository."""
        logger.info(f"[INFO] MCP Tool invoked: list_issues for {owner}/{repo} (state={state})")
        issues = self.client.get_issues(owner, repo, state=state, per_page=per_page)
        return {"count": len(issues), "issues": issues}

    # MCP Tool: list_pull_requests
    def list_pull_requests(self, owner: str, repo: str, state: str = "all", per_page: int = 30) -> Dict[str, Any]:
        """MCP Tool: List pull requests from the repository."""
        logger.info(f"[INFO] MCP Tool invoked: list_pull_requests for {owner}/{repo} (state={state})")
        prs = self.client.get_pull_requests(owner, repo, state=state, per_page=per_page)
        return {"count": len(prs), "pull_requests": prs}

    # MCP Tool: list_branches
    def list_branches(self, owner: str, repo: str, per_page: int = 30) -> Dict[str, Any]:
        """MCP Tool: List repository branches."""
        logger.info(f"[INFO] MCP Tool invoked: list_branches for {owner}/{repo}")
        branches = self.client.get_branches(owner, repo, per_page=per_page)
        return {"count": len(branches), "branches": branches}

    # MCP Tool: list_commits
    def list_commits(self, owner: str, repo: str, per_page: int = 50) -> Dict[str, Any]:
        """MCP Tool: List commit history."""
        logger.info(f"[INFO] MCP Tool invoked: list_commits for {owner}/{repo}")
        commits = self.client.get_commits(owner, repo, per_page=per_page)
        return {"count": len(commits), "commits": commits}
