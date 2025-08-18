"""Decision helpers for the bumpwright CLI."""

from __future__ import annotations

import argparse
import json
import logging
import os
from collections.abc import Iterable
from fnmatch import fnmatch

from ..analysers import get_analyser_info
from ..compare import Decision, Impact, decide_bump, diff_public_api
from ..config import Config, load_config
from ..gitutils import (
    GitCommandError,
    changed_paths,
    format_git_error,
    last_release_commit,
    list_py_files_at_ref,
    read_file_at_ref,
    run_git,
)
from ..public_api import build_api_at_ref, parse_python_source
from ..versioning import bump_string, read_project_version
from . import _env_flag, _env_list, add_analyser_toggles, add_ref_options
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
        default=os.getenv("BUMPWRIGHT_FORMAT", "text"),
        help="Output style: plain text, Markdown, or machine-readable JSON.",
    )
    parser.add_argument(
        "--emit-changelog",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_EMIT_CHANGELOG"),
        help="Print expected changelog for the suggested version.",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_EXPLAIN"),
        help="Show reasoning behind the selected bump level.",
    )
    parser.add_argument(
        "--no-impl-change-patch",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_NO_IMPL_CHANGE_PATCH"),
        help="Ignore implementation-only changes to public symbols.",
    )
    parser.add_argument(
        "--repo-url",
        default=os.getenv("BUMPWRIGHT_REPO_URL"),
        help=(
            "Base repository URL for linking commit hashes in Markdown output. "
            "Can also be set via [changelog].repo_url in configuration."
        ),
    )
    parser.add_argument(
        "--changelog-template",
        default=os.getenv("BUMPWRIGHT_CHANGELOG_TEMPLATE"),
        help=(
            "Jinja2 template file for changelog entries; defaults to the built-in "
            "template or [changelog].template when configured."
        ),
    )
    parser.add_argument(
        "--changelog-exclude",
        action="append",
        default=_env_list("BUMPWRIGHT_CHANGELOG_EXCLUDE"),
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


def _extra_file_impacts(base: str, head: str, cfg: Config) -> list[Impact]:
    """Return impacts for configured extra public files.

    Args:
        base: Base git reference.
        head: Head git reference.
        cfg: Loaded configuration object.

    Returns:
        List of patch-level impacts for files matching
        ``cfg.project.extra_public_files``.
    """

    changed = changed_paths(base, head)
    impacts: list[Impact] = []
    for pat in cfg.project.extra_public_files:
        for path in changed:
            if fnmatch(path, pat):
                impacts.append(Impact("patch", path, "Modified public file"))
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


def _collect_impacts(
    base: str, head: str, cfg: Config, args: argparse.Namespace
) -> list[Impact]:
    """Gather impacts between two git references.

    Args:
        base: Base git reference for comparison.
        head: Head git reference for comparison.
        cfg: Project configuration object.
        args: Parsed command-line arguments containing analyser toggles.

    Returns:
        List of detected impacts.
    """

    old_api = build_api_at_ref(
        base, cfg.project.public_roots, cfg.ignore.paths, cfg.project.private_prefixes
    )
    new_api = build_api_at_ref(
        head, cfg.project.public_roots, cfg.ignore.paths, cfg.project.private_prefixes
    )
    body_change = cfg.rules.implementation_change
    if getattr(args, "no_impl_change_patch", False):
        body_change = None
    impacts = diff_public_api(
        old_api,
        new_api,
        return_type_change=cfg.rules.return_type_change,
        param_annotation_change=cfg.rules.param_annotation_change,
        body_change=body_change,
    )
    impacts.extend(
        _run_analysers(base, head, cfg, args.enable_analyser, args.disable_analyser)
    )
    impacts.extend(_extra_file_impacts(base, head, cfg))
    return impacts


def _log_explanation(impacts: list[Impact], cfg: Config, decision: Decision) -> None:
    """Log reasoning behind the selected bump level."""

    logger.info("Detected impacts:\n%s", _format_impacts_text(impacts))
    logger.info(
        "Applied rules: return_type_change=%s, param_annotation_change=%s, implementation_change=%s",
        cfg.rules.return_type_change,
        cfg.rules.param_annotation_change,
        cfg.rules.implementation_change,
    )
    logger.info("Chosen bump level: %s", decision.level)


def _infer_base_ref() -> str:
    """Determine the upstream git reference for the current branch."""

    try:
        res = run_git(
            [
                "rev-parse",
                "--abbrev-ref",
                "--symbolic-full-name",
                "@{u}",
            ]
        )
        return res.stdout.strip()
    except GitCommandError as exc:
        logger.warning(format_git_error("Failed to determine upstream ref", exc))
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
        new_version = (
            bump_string(old_version, decision.level, cfg.version.scheme)
            if decision.level
            else old_version
        )
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
