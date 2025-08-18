"""Environment variable defaults for CLI options."""

from __future__ import annotations

import pytest

from bumpwright.cli import get_parser


def test_global_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use environment variables for global flags."""

    monkeypatch.setenv("BUMPWRIGHT_CONFIG", "custom.toml")
    monkeypatch.setenv("BUMPWRIGHT_QUIET", "1")
    parser = get_parser()
    args = parser.parse_args([])
    assert args.config == "custom.toml"
    assert args.quiet is True


def test_subparser_env_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure subparser options honour environment defaults."""

    monkeypatch.setenv("BUMPWRIGHT_REPO_URL", "https://example.com")
    parser = get_parser()
    args = parser.parse_args(["bump"])
    assert args.repo_url == "https://example.com"


def test_env_list_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Parse comma-separated environment variables for repeatable flags."""

    monkeypatch.setenv("BUMPWRIGHT_ENABLE_ANALYSER", "cli,db")
    parser = get_parser()
    args = parser.parse_args(["bump"])
    assert args.enable_analyser == ["cli", "db"]
