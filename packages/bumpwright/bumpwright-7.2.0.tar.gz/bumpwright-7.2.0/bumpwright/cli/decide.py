"""Decision helpers for the bumpwright CLI."""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
from collections.abc import Iterable

from ..analysers import get_analyser_info
from ..compare import Decision, Impact, decide_bump, diff_public_api
from ..config import Config, load_config
from ..gitutils import last_release_commit, list_py_files_at_ref, read_file_at_ref
from ..public_api import build_api_at_ref, parse_python_source
from ..versioning import bump_string, read_project_version
from . import add_analyser_toggles, add_ref_options
from .changelog import _build_changelog

logger = logging.getLogger(__name__)


def _format_impacts_text(impacts: list[Impact]) -> str:
    """Render a list of impacts as human-readable text."""

    lines = []
    for i in impacts:
        lines.append(f"- [{i.severity.upper()}] {i.symbol}: {i.reason}")
    return "\n".join(lines) if lines else "(no API-impacting changes detected)"


def add_decide_arguments(parser: argparse.ArgumentParser) -> None:
    """Add shared decision-related CLI options to ``parser``.

    Args:
        parser: The parser to extend with ref and analyser options.

    Example:
        >>> import argparse
        >>> p = argparse.ArgumentParser()
        >>> add_decide_arguments(p)
        >>> '--format' in p.format_help()
        True
    """

    add_ref_options(parser)
    parser.add_argument(
        "--format",
        choices=["text", "md", "json"],
        default="text",
        help="Output style: plain text, Markdown, or machine-readable JSON.",
    )
    parser.add_argument(
        "--emit-changelog",
        action="store_true",
        help="Print expected changelog for the suggested version.",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Show reasoning behind the selected bump level.",
    )
    parser.add_argument(
        "--repo-url",
        help=(
            "Base repository URL for linking commit hashes in Markdown output. "
            "Can also be set via [changelog].repo_url in configuration."
        ),
    )
    parser.add_argument(
        "--changelog-template",
        help=(
            "Jinja2 template file for changelog entries; defaults to the built-in "
            "template or [changelog].template when configured."
        ),
    )
    parser.add_argument(
        "--changelog-exclude",
        action="append",
        help=(
            "Regex pattern for commit subjects to exclude from changelog "
            "(repeatable). Combined with patterns from [changelog].exclude."
        ),
    )
    add_analyser_toggles(parser)


def _run_analysers(
    base: str,
    head: str,
    cfg: Config,
    enable: Iterable[str] | None = None,
    disable: Iterable[str] | None = None,
) -> list[Impact]:
    """Run analyser plugins and collect impacts."""

    names = set(cfg.analysers.enabled)
    if enable:
        names.update(enable)
    if disable:
        names.difference_update(disable)

    impacts: list[Impact] = []
    for name in names:
        info = get_analyser_info(name)
        if info is None:
            logger.warning("Analyser '%s' is not registered", name)
            continue
        analyser = info.cls(cfg)
        old = analyser.collect(base)
        new = analyser.collect(head)
        impacts.extend(analyser.compare(old, new))
    return impacts


def _build_api_at_ref(
    ref: str,
    roots: Iterable[str],
    ignore_globs: Iterable[str],
    private_prefixes: Iterable[str],
) -> dict[str, str]:
    """Build a public API mapping for ``ref``.

    Args:
        ref: Git reference to inspect.
        roots: Root directories to include.
        ignore_globs: Glob patterns to exclude.
        private_prefixes: Symbol prefixes considered private.

    Returns:
        Mapping of symbol identifiers to definitions.
    """

    api: dict[str, str] = {}
    for path in list_py_files_at_ref(ref, roots, ignore_globs=ignore_globs):
        src = read_file_at_ref(ref, path)
        if src is None:
            continue
        parsed = parse_python_source(src)
        if parsed is None:
            continue
        api.update(parsed)
    return api


def _collect_impacts(base: str, head: str, cfg: Config, args: argparse.Namespace) -> list[Impact]:
    """Gather impacts between two git references.

    Args:
        base: Base git reference for comparison.
        head: Head git reference for comparison.
        cfg: Project configuration object.
        args: Parsed command-line arguments containing analyser toggles.

    Returns:
        List of detected impacts.
    """

    old_api = build_api_at_ref(base, cfg.project.public_roots, cfg.ignore.paths, cfg.project.private_prefixes)
    new_api = build_api_at_ref(head, cfg.project.public_roots, cfg.ignore.paths, cfg.project.private_prefixes)
    impacts = diff_public_api(
        old_api,
        new_api,
        return_type_change=cfg.rules.return_type_change,
        param_annotation_change=cfg.rules.param_annotation_change,
    )
    impacts.extend(_run_analysers(base, head, cfg, args.enable_analyser, args.disable_analyser))
    return impacts


def _log_explanation(impacts: list[Impact], cfg: Config, decision: Decision) -> None:
    """Log reasoning behind the selected bump level."""

    logger.info("Detected impacts:\n%s", _format_impacts_text(impacts))
    logger.info(
        "Applied rules: return_type_change=%s, param_annotation_change=%s",
        cfg.rules.return_type_change,
        cfg.rules.param_annotation_change,
    )
    logger.info("Chosen bump level: %s", decision.level)


def _infer_base_ref() -> str:
    """Determine the upstream git reference for the current branch."""

    try:
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        return res.stdout.strip()
    except subprocess.CalledProcessError:
        return "origin/HEAD"


def _decide_only(args: argparse.Namespace, cfg: Config) -> int:
    """Compute and display the suggested bump level."""

    base = args.base or last_release_commit() or "HEAD^"
    head = args.head
    impacts = _collect_impacts(base, head, cfg, args)
    decision = decide_bump(impacts)
    if getattr(args, "explain", False):
        _log_explanation(impacts, cfg, decision)
    changelog = None
    if getattr(args, "emit_changelog", False):
        args.changelog = "-"
        old_version = read_project_version()
        new_version = bump_string(old_version, decision.level, cfg.version.scheme) if decision.level else old_version
        changelog = _build_changelog(args, new_version)
    payload = {
        "level": decision.level,
        "confidence": decision.confidence,
        "reasons": decision.reasons,
        "impacts": [i.__dict__ for i in impacts],
    }
    if changelog is not None:
        payload["changelog"] = changelog
    if args.format == "json":
        logger.info(json.dumps(payload, indent=2))
    elif args.format == "md":
        logger.info("**bumpwright** suggests: `%s`\n", decision.level)
        logger.info("%s", _format_impacts_text(impacts))
        if changelog:
            logger.info("\n%s", changelog.rstrip())
    else:
        logger.info("Suggested bump: %s", decision.level)
        logger.info("%s", _format_impacts_text(impacts))
        if changelog:
            logger.info("\n%s", changelog.rstrip())
    return 0


def _infer_level(
    base: str,
    head: str,
    cfg: Config,
    args: argparse.Namespace,
) -> Decision:
    """Compute bump level from repository differences."""
    impacts = _collect_impacts(base, head, cfg, args)
    decision = decide_bump(impacts)
    if getattr(args, "explain", False):
        _log_explanation(impacts, cfg, decision)
    return decision


def decide_command(args: argparse.Namespace) -> int:
    """Compute and display the suggested version bump.

    Args:
        args: Parsed command-line arguments for the ``decide`` command.

    Returns:
        Exit status code. ``0`` indicates success.
    """

    cfg: Config = load_config(args.config)
    if getattr(args, "repo_url", None) is None and cfg.changelog.repo_url:
        args.repo_url = cfg.changelog.repo_url
    if getattr(args, "changelog_template", None) is None and cfg.changelog.template:
        args.changelog_template = cfg.changelog.template
    excludes = list(cfg.changelog.exclude)
    cli_excludes = getattr(args, "changelog_exclude", []) or []
    excludes.extend(cli_excludes)
    args.changelog_exclude = excludes
    if args.emit_changelog:
        args.changelog = "-"
    else:
        args.changelog = None
    return _decide_only(args, cfg)
