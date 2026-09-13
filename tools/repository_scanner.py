"""Repository scanning tool to inspect structure, languages, manifests, and entry points."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.repository import RepositoryRef, RepositoryMetadata, RepositoryStructure, RepositoryOverview
from tools.github_client import GitHubClient

logger = logging.getLogger("agentic_github_analyzer.repository_scanner")

KNOWN_MANIFESTS = {
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "Pipfile": "Python",
    "setup.py": "Python",
    "package.json": "JavaScript/TypeScript",
    "tsconfig.json": "TypeScript",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "pom.xml": "Java",
    "build.gradle": "Java/Kotlin",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "Makefile": "Make",
    ".env.example": "Environment Configuration",
}

ENTRY_POINT_CANDIDATES = [
    "main.py", "app.py", "cli.py", "run.py", "server.py", "__main__.py",
    "index.js", "index.ts", "server.js", "server.ts", "app.js", "app.ts", "main.ts",
    "main.go", "index.php"
]

IMPORTANT_DIR_KEYWORDS = [
    "src", "app", "lib", "core", "pkg", "cmd", "internal",
    "api", "services", "models", "controllers", "tools", "agents",
    "tests", "test", "docs", "config", "frontend", "backend", "web"
]


class RepositoryScanner:
    """Discovers and catalogs repository structure and metadata."""

    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client or GitHubClient()

    def scan(self, repo_ref: RepositoryRef) -> RepositoryOverview:
        """Perform comprehensive repository discovery."""
        logger.info(f"[INFO] Scanning repository metadata for {repo_ref.full_name}")
        raw_meta = self.client.get_repository(repo_ref.owner, repo_ref.repo)
        languages_dict = self.client.get_languages(repo_ref.owner, repo_ref.repo)

        # Parse datetime strings
        created_at = datetime.fromisoformat(raw_meta["created_at"].replace("Z", "+00:00")) if raw_meta.get("created_at") else None
        updated_at = datetime.fromisoformat(raw_meta["updated_at"].replace("Z", "+00:00")) if raw_meta.get("updated_at") else None
        pushed_at = datetime.fromisoformat(raw_meta["pushed_at"].replace("Z", "+00:00")) if raw_meta.get("pushed_at") else None

        license_name = None
        if raw_meta.get("license") and isinstance(raw_meta["license"], dict):
            license_name = raw_meta["license"].get("name") or raw_meta["license"].get("spdx_id")

        metadata = RepositoryMetadata(
            name=raw_meta.get("name", repo_ref.repo),
            full_name=raw_meta.get("full_name", repo_ref.full_name),
            description=raw_meta.get("description"),
            default_branch=raw_meta.get("default_branch", "main"),
            stars_count=raw_meta.get("stargazers_count", 0),
            forks_count=raw_meta.get("forks_count", 0),
            open_issues_count=raw_meta.get("open_issues_count", 0),
            subscribers_count=raw_meta.get("subscribers_count", 0),
            license_name=license_name,
            created_at=created_at,
            updated_at=updated_at,
            pushed_at=pushed_at,
            is_private=raw_meta.get("private", False),
            is_archived=raw_meta.get("archived", False),
            is_fork=raw_meta.get("fork", False),
            homepage=raw_meta.get("homepage"),
            topics=raw_meta.get("topics", [])
        )

        # Scan repository tree
        logger.info(f"[INFO] Fetching recursive file tree on default branch '{metadata.default_branch}'")
        tree = self.client.get_git_tree(repo_ref.owner, repo_ref.repo, branch=metadata.default_branch)

        important_dirs = set()
        config_files = []
        entry_points = []
        manifests = []
        readme_path = None
        docker_present = False
        ci_cd_present = False

        for item in tree:
            path = item.get("path", "")
            item_type = item.get("type", "")
            lower_path = path.lower()

            if item_type == "tree":
                # Directory
                parts = path.split("/")
                top_dir = parts[0]
                if top_dir.lower() in IMPORTANT_DIR_KEYWORDS:
                    important_dirs.add(top_dir)
                if ".github" in parts:
                    ci_cd_present = True

            elif item_type == "blob":
                # File
                filename = path.split("/")[-1]
                lower_filename = filename.lower()

                # README detection
                if lower_filename.startswith("readme."):
                    readme_path = path

                # Docker detection
                if "dockerfile" in lower_filename or "docker-compose" in lower_filename:
                    docker_present = True

                # Manifest / config detection
                if filename in KNOWN_MANIFESTS or lower_filename in KNOWN_MANIFESTS:
                    config_files.append(path)
                    manifests.append(filename)
                elif filename.startswith(".env.") or filename == ".env":
                    config_files.append(path)

                # Entry point detection
                if filename in ENTRY_POINT_CANDIDATES:
                    entry_points.append(path)
                elif ("cmd/" in path or "main.go" in path) and path not in entry_points:
                    entry_points.append(path)

        sorted_languages = sorted(languages_dict.keys(), key=lambda k: languages_dict[k], reverse=True)
        if not sorted_languages and raw_meta.get("language"):
            sorted_languages = [raw_meta["language"]]

        structure = RepositoryStructure(
            repository=repo_ref.full_name,
            languages=sorted_languages,
            language_distribution=languages_dict,
            important_directories=sorted(list(important_dirs)),
            config_files=sorted(config_files),
            entry_points=sorted(entry_points),
            manifest_files=sorted(manifests),
            readme_present=bool(readme_path),
            readme_path=readme_path,
            docker_present=docker_present,
            ci_cd_present=ci_cd_present,
            total_files_scanned=len(tree)
        )

        return RepositoryOverview(metadata=metadata, structure=structure)
