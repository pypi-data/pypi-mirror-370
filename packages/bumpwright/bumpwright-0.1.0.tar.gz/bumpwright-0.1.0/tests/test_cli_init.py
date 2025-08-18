from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import pytest
from cli_helpers import run, setup_repo

from bumpwright.cli.init import init_command
from bumpwright.gitutils import last_release_commit


def test_init_outputs_summary_json(tmp_path: Path) -> None:
    """``bumpwright init --summary json`` reports version and symbols."""

    repo, _pkg, _base = setup_repo(tmp_path)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "init",
            "--summary",
            "json",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    out = res.stdout
    json_start = out.find("{")
    data = json.loads(out[json_start:])
    assert data["version"] == "0.1.0"
    assert "__init__:foo" in data["public_symbols"]
    assert data["changes"] == []


def test_init_outputs_summary_table(tmp_path: Path) -> None:
    """Human-readable summary is printed in table format."""

    repo, _pkg, _base = setup_repo(tmp_path)
    env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[1])}
    res = subprocess.run(
        [
            sys.executable,
            "-m",
            "bumpwright.cli",
            "init",
            "--summary",
        ],
        cwd=repo,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    out = res.stdout
    assert "Version" in out and "Public symbols" in out
    assert "__init__:foo" in out
    assert "No API-impacting changes" in out
    msg = run(["git", "log", "-1", "--format=%s"], repo)
    assert msg == "chore(release): initialise baseline"
    head = run(["git", "rev-parse", "HEAD"], repo)
    assert last_release_commit(str(repo)) == head


def test_init_command_baseline_exists(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Skip commit when a baseline already exists."""

    monkeypatch.setattr("bumpwright.cli.init.last_release_commit", lambda: "abc")
    with caplog.at_level(logging.INFO):
        status = init_command(argparse.Namespace())
    assert status == 0
    assert "Baseline already initialised." in caplog.text
