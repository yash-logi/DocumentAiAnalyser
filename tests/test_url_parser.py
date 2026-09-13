"""Unit tests for GitHub URL parsing and validation."""

import pytest
from tools.github_client import parse_github_url


def test_parse_valid_https_url():
    ref = parse_github_url("https://github.com/psf/requests")
    assert ref.owner == "psf"
    assert ref.repo == "requests"


def test_parse_https_url_with_git_suffix():
    ref = parse_github_url("https://github.com/pallets/flask.git")
    assert ref.owner == "pallets"
    assert ref.repo == "flask"


def test_parse_https_url_with_trailing_slash():
    ref = parse_github_url("https://github.com/torvalds/linux/")
    assert ref.owner == "torvalds"
    assert ref.repo == "linux"


def test_parse_ssh_url():
    ref = parse_github_url("git@github.com:facebook/react.git")
    assert ref.owner == "facebook"
    assert ref.repo == "react"


def test_parse_short_owner_repo():
    ref = parse_github_url("openai/whisper")
    assert ref.owner == "openai"
    assert ref.repo == "whisper"


def test_parse_invalid_host():
    with pytest.raises(ValueError, match="Unsupported host"):
        parse_github_url("https://gitlab.com/owner/repo")


def test_parse_invalid_format():
    with pytest.raises(ValueError):
        parse_github_url("not_a_url")


def test_parse_empty_string():
    with pytest.raises(ValueError):
        parse_github_url("")
