from argparse import ArgumentParser

from bumpwright.cli import (
    _build_bump_subparser,
    _build_decide_subparser,
    _build_init_subparser,
    bump_command,
    decide_command,
    init_command,
)


def test_build_init_subparser_registers_command() -> None:
    """Ensure the ``init`` subparser is configured correctly."""

    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    init_parser = _build_init_subparser(sub)

    assert sub.choices["init"] is init_parser
    assert init_parser.get_default("func") is init_command


def test_build_bump_subparser_registers_arguments() -> None:
    """Validate ``bump`` subparser argument registration."""

    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    bump_parser = _build_bump_subparser(sub)

    assert sub.choices["bump"] is bump_parser
    assert bump_parser.get_default("func") is bump_command

    dests = {action.dest for action in bump_parser._actions}
    expected = {
        "base",
        "head",
        "enable_analyser",
        "disable_analyser",
        "format",
        "repo_url",
        "pyproject",
        "version_path",
        "version_ignore",
        "commit",
        "tag",
        "dry_run",
        "changelog",
        "changelog_template",
        "changelog_exclude",
        "explain",
    }
    assert expected <= dests


def test_build_decide_subparser_registers_command() -> None:
    """Validate ``decide`` subparser argument registration."""

    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")
    decide_parser = _build_decide_subparser(sub)

    assert sub.choices["decide"] is decide_parser
    assert decide_parser.get_default("func") is decide_command
    dests = {action.dest for action in decide_parser._actions}
    assert {"base", "head", "format", "emit_changelog", "explain"} <= dests
