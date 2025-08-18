import argparse
import os
from pathlib import Path

import pytest
from cli_helpers import run, setup_repo

from bumpwright.cli.decide import _collect_impacts
from bumpwright.compare import decide_bump
from bumpwright.config import load_config
from bumpwright.gitutils import _list_py_files_at_ref_cached


@pytest.mark.parametrize("impl_change", [None, "minor", "major"])
def test_extra_public_file_triggers_patch(
    tmp_path: Path, impl_change: str | None
) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    config = "[project]\n" "public_roots=['pkg']\n" "extra_public_files=['docs/*.md']\n"
    (repo / "bumpwright.toml").write_text(config, encoding="utf-8")
    run(["git", "commit", "-am", "chore: configure extra public files"], repo)

    docs = repo / "docs"
    docs.mkdir()
    doc = docs / "guide.md"
    doc.write_text("old", encoding="utf-8")
    run(["git", "add", "docs/guide.md"], repo)
    run(["git", "commit", "-m", "docs: add guide"], repo)

    doc.write_text("new", encoding="utf-8")
    run(["git", "commit", "-am", "docs: update guide"], repo)

    cfg = load_config(repo / "bumpwright.toml")
    cfg.rules.implementation_change = impl_change
    args = argparse.Namespace(
        enable_analyser=None, disable_analyser=None, no_impl_change_patch=False
    )
    prev_cwd = Path.cwd()
    try:
        os.chdir(repo)
        _list_py_files_at_ref_cached.cache_clear()
        impacts = _collect_impacts("HEAD^", "HEAD", cfg, args)
    finally:
        os.chdir(prev_cwd)
    decision = decide_bump(impacts)
    assert decision.level == "patch"
    assert decision.reasons == ["Modified public file"]
