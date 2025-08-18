import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from cli_helpers import run, setup_repo


def _run_bump(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Execute the ``bump`` CLI with provided arguments."""
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    return subprocess.run(
        [sys.executable, "-m", "bumpwright.cli", "bump", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )


def _run_decide(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Execute the ``decide`` CLI with provided arguments."""

    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    return subprocess.run(
        [sys.executable, "-m", "bumpwright.cli", "decide", *args],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )


def test_bump_twice_no_new_changes(tmp_path: Path) -> None:
    """Running ``bump`` twice without new commits does nothing."""
    repo, pkg, _ = setup_repo(tmp_path)
    init_file = pkg / "__init__.py"
    init_file.write_text("def foo() -> float:\n    return 1.0\n", encoding="utf-8")
    run(["git", "add", "pkg/__init__.py"], repo)
    run(["git", "commit", "-m", "fix: return type"], repo)

    _run_bump(repo, "--commit")

    head_before = run(["git", "rev-parse", "HEAD"], repo)
    res = _run_bump(repo, "--commit")
    assert "No version bump needed" in res.stderr
    head_after = run(["git", "rev-parse", "HEAD"], repo)
    assert head_after == head_before
    assert run(["git", "status", "--porcelain"], repo) == ""


def test_decide_twice_no_new_changes(tmp_path: Path) -> None:
    """``decide`` remains stable when run multiple times."""
    repo, pkg, _ = setup_repo(tmp_path)
    init_file = pkg / "__init__.py"
    init_file.write_text("def foo() -> float:\n    return 1.0\n", encoding="utf-8")
    run(["git", "add", "pkg/__init__.py"], repo)
    run(["git", "commit", "-m", "fix: return type"], repo)

    _run_bump(repo, "--commit")

    head_before = run(["git", "rev-parse", "HEAD"], repo)
    _run_decide(repo)
    res = _run_decide(repo)
    assert "Suggested bump: None" in res.stderr
    head_after = run(["git", "rev-parse", "HEAD"], repo)
    assert head_after == head_before
    assert run(["git", "status", "--porcelain"], repo) == ""


def test_calver_bump_twice_no_new_changes(tmp_path: Path) -> None:
    """CalVer patch bumps are idempotent."""
    today = date.today()
    version = f"{today.year}.{today.month:02d}.0"
    repo, pkg, _ = setup_repo(tmp_path, version=version, scheme="calver")
    init_file = pkg / "__init__.py"
    init_file.write_text("def foo() -> float:\n    return 1.0\n", encoding="utf-8")
    run(["git", "add", "pkg/__init__.py"], repo)
    run(["git", "commit", "-m", "fix: return type"], repo)

    _run_bump(repo, "--commit")

    head_before = run(["git", "rev-parse", "HEAD"], repo)
    res = _run_bump(repo, "--commit")
    assert "No version bump needed" in res.stderr
    head_after = run(["git", "rev-parse", "HEAD"], repo)
    assert head_after == head_before
    assert run(["git", "status", "--porcelain"], repo) == ""


def test_calver_decide_twice_no_new_changes(tmp_path: Path) -> None:
    """``decide`` with CalVer reports no bump on repeated runs."""
    today = date.today()
    version = f"{today.year}.{today.month:02d}.0"
    repo, pkg, _ = setup_repo(tmp_path, version=version, scheme="calver")
    init_file = pkg / "__init__.py"
    init_file.write_text("def foo() -> float:\n    return 1.0\n", encoding="utf-8")
    run(["git", "add", "pkg/__init__.py"], repo)
    run(["git", "commit", "-m", "fix: return type"], repo)

    _run_bump(repo, "--commit")

    head_before = run(["git", "rev-parse", "HEAD"], repo)
    _run_decide(repo)
    res = _run_decide(repo)
    assert "Suggested bump: None" in res.stderr
    head_after = run(["git", "rev-parse", "HEAD"], repo)
    assert head_after == head_before
    assert run(["git", "status", "--porcelain"], repo) == ""
