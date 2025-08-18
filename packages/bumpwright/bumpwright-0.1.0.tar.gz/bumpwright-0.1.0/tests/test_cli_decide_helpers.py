"""Additional tests for CLI decide helpers."""

import argparse
import logging

import pytest

from bumpwright.cli import decide
from bumpwright.compare import Decision
from bumpwright.config import Config


def test_build_api_skips_unparsed_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Files that fail to parse are ignored."""

    monkeypatch.setattr(decide, "list_py_files_at_ref", lambda ref, roots, ignore_globs=None: ["mod.py"])
    monkeypatch.setattr(decide, "parse_python_source", lambda ref, path: None)
    api = decide._build_api_at_ref("HEAD", ["."], [], [])
    assert api == {}


def test_add_decide_arguments_includes_format() -> None:
    """Parser gains the ``--format`` option with default ``text``."""

    parser = argparse.ArgumentParser()
    decide.add_decide_arguments(parser)
    args = parser.parse_args([])
    assert args.format == "text"


def test_decide_only_md_format(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    """Markdown output is produced when requested."""

    cfg = Config()
    args = argparse.Namespace(
        base=None,
        head="HEAD",
        enable_analyser=None,
        disable_analyser=None,
        format="md",
        explain=False,
    )
    monkeypatch.setattr(decide, "_collect_impacts", lambda b, h, c, a: [])
    monkeypatch.setattr(decide, "decide_bump", lambda impacts: Decision("patch", 1.0, []))
    with caplog.at_level(logging.INFO):
        assert decide._decide_only(args, cfg) == 0
    assert "**bumpwright** suggests" in caplog.text
