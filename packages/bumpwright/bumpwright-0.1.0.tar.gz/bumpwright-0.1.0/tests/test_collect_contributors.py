from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "bumpwright"

spec = importlib.util.spec_from_file_location("gitutils", PACKAGE_ROOT / "gitutils.py")
gitutils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gitutils)


def test_collect_contributors(tmp_path: Path) -> None:
    """Collect contributors between two commits."""

    repo = tmp_path / "repo"
    repo.mkdir()
    file = repo / "file.txt"
    file.write_text("init\n", encoding="utf-8")
    gitutils._run(["git", "init"], str(repo))
    gitutils._run(["git", "config", "user.email", "test@example.com"], str(repo))
    gitutils._run(["git", "config", "user.name", "Test"], str(repo))
    gitutils._run(["git", "add", "file.txt"], str(repo))
    gitutils._run(["git", "commit", "-m", "init"], str(repo))
    file.write_text("alice\n", encoding="utf-8")
    gitutils._run(
        [
            "git",
            "commit",
            "-am",
            "alice",
            "--author",
            "Alice <alice@example.com>",
        ],
        str(repo),
    )
    file.write_text("bob\n", encoding="utf-8")
    gitutils._run(
        [
            "git",
            "commit",
            "-am",
            "bob",
            "--author",
            "Bob <bob@example.com>",
        ],
        str(repo),
    )
    contributors = gitutils.collect_contributors("HEAD~2", "HEAD", str(repo))
    assert contributors == [
        ("Alice", "alice@example.com"),
        ("Bob", "bob@example.com"),
    ]


def test_collect_contributors_invalid_ref(tmp_path: Path) -> None:
    """Invalid references raise ``CalledProcessError``."""

    repo = tmp_path / "repo"
    repo.mkdir()
    file = repo / "file.txt"
    file.write_text("init\n", encoding="utf-8")
    gitutils._run(["git", "init"], str(repo))
    gitutils._run(["git", "config", "user.email", "test@example.com"], str(repo))
    gitutils._run(["git", "config", "user.name", "Test"], str(repo))
    gitutils._run(["git", "add", "file.txt"], str(repo))
    gitutils._run(["git", "commit", "-m", "init"], str(repo))

    with pytest.raises(subprocess.CalledProcessError):
        gitutils.collect_contributors("BAD", "HEAD", str(repo))
