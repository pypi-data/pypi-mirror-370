import argparse
import logging
import subprocess
from pathlib import Path

import pytest
from cli_helpers import run, setup_repo

from bumpwright.cli.bump import bump_command


def _args(commit: bool = False, tag: bool = False) -> argparse.Namespace:
    """Build argument namespace for ``bump_command`` tests."""

    return argparse.Namespace(
        config="bumpwright.toml",
        base=None,
        head="HEAD",
        format="text",
        repo_url=None,
        enable_analyser=[],
        disable_analyser=[],
        pyproject="pyproject.toml",
        version_path=[],
        version_ignore=[],
        commit=commit,
        tag=tag,
        dry_run=False,
        changelog=None,
        changelog_template=None,
        changelog_exclude=[],
    )


def _prepare_repo(tmp_path: Path) -> Path:
    repo, pkg, _ = setup_repo(tmp_path)
    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    return repo


def test_bump_commit_failure(
    monkeypatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Return ``1`` and log an error when committing fails."""

    repo = _prepare_repo(tmp_path)

    def fail(
        args: list[str], cwd: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        if args[0] == "commit":
            raise subprocess.CalledProcessError(1, ["git", *args], stderr="boom")
        return subprocess.CompletedProcess(["git", *args], 0, "", "")

    monkeypatch.setattr("bumpwright.cli.bump.run_git", fail)
    monkeypatch.chdir(repo)
    with caplog.at_level(logging.ERROR):
        res = bump_command(_args(commit=True))
    assert res == 1
    assert "Failed to commit release" in caplog.text


def test_bump_tag_failure(
    monkeypatch, tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Return ``1`` and log an error when tagging fails."""

    repo = _prepare_repo(tmp_path)

    def fail(
        args: list[str], cwd: str | None = None
    ) -> subprocess.CompletedProcess[str]:
        if args[0] == "tag":
            raise subprocess.CalledProcessError(1, ["git", *args], stderr="boom")
        return subprocess.CompletedProcess(["git", *args], 0, "", "")

    monkeypatch.setattr("bumpwright.cli.bump.run_git", fail)
    monkeypatch.chdir(repo)
    with caplog.at_level(logging.ERROR):
        res = bump_command(_args(tag=True))
    assert res == 1
    assert "Failed to create tag" in caplog.text
