import os
import subprocess
import sys
from pathlib import Path

from cli_helpers import run, setup_repo


def _run_history(repo: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    return subprocess.run(
        [sys.executable, "-m", "bumpwright.cli", "history"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )


def test_history_lists_tags(tmp_path: Path) -> None:
    """History subcommand lists existing git tags."""
    repo, _, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    res = _run_history(repo)
    assert "v0.1.0 0.1.0" in res.stderr


def test_history_warns_on_mismatch(tmp_path: Path) -> None:
    """Warn when project version differs from the latest tag."""
    repo, _, _ = setup_repo(tmp_path)
    run(["git", "tag", "v0.1.0"], repo)
    (repo / "pyproject.toml").write_text(
        """[project]\nname='demo'\nversion='0.2.0'\n""",
        encoding="utf-8",
    )
    res = _run_history(repo)
    assert "Project version 0.2.0 differs from latest tag 0.1.0" in res.stderr
