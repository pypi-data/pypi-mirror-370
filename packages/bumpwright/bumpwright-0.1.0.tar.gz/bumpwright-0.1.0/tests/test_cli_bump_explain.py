import os
import subprocess
import sys
from pathlib import Path

from cli_helpers import run, setup_repo


def _env() -> dict[str, str]:
    root = Path(__file__).resolve().parents[1]
    return {**os.environ, "PYTHONPATH": str(root)}


def test_bump_explain_outputs_details(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    res = subprocess.run(
        [sys.executable, "-m", "bumpwright.cli", "bump", "--dry-run", "--explain"],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=_env(),
    )
    assert "Applied rules: return_type_change=minor, param_annotation_change=patch" in res.stderr
    assert "Detected impacts" in res.stderr and "Added public symbol" in res.stderr
    assert "Chosen bump level: minor" in res.stderr


def test_decide_explain_outputs_details(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    (pkg / "extra.py").write_text("def bar() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add bar"], repo)
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "decide",
            "--explain",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=_env(),
    )
    assert "Applied rules: return_type_change=minor, param_annotation_change=patch" in res.stderr
    assert "Detected impacts" in res.stderr and "Added public symbol" in res.stderr
    assert "Chosen bump level: minor" in res.stderr
