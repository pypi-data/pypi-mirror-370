import json
import os
import subprocess
import sys
from pathlib import Path

from cli_helpers import run, setup_repo


def test_bump_command_json_format(tmp_path: Path) -> None:
    """Ensure bump emits machine-readable JSON when requested."""
    repo, _, _ = setup_repo(tmp_path)
    (repo / "pkg" / "extra.py").write_text(
        "def bar() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: change"], repo)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "bump",
            "--pyproject",
            "pyproject.toml",
            "--dry-run",
            "--format",
            "json",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    data = json.loads(res.stderr)
    assert data["old_version"] == "0.1.0"
    assert data["new_version"] == "0.2.0"
    assert data["level"] == "minor"
    assert data["confidence"] == 1.0
    assert isinstance(data["reasons"], list)
