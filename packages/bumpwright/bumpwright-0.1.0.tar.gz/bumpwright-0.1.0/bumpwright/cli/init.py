"""Initialisation command for the bumpwright CLI."""

from __future__ import annotations

import argparse
import json
import logging

from ..compare import diff_public_api
from ..config import load_config
from ..gitutils import (
    GitCommandError,
    format_git_error,
    last_release_commit,
    run_git,
)
from ..public_api import build_api_at_ref
from ..versioning import read_project_version

logger = logging.getLogger(__name__)


def _format_table(rows: list[tuple[str, str]]) -> str:
    """Render ``rows`` as an ASCII table."""

    col1 = max(len(k) for k, _ in rows)
    col2 = max(len(v) for _, v in rows)
    border = f"+{'-' * (col1 + 2)}+{'-' * (col2 + 2)}+"
    lines = [border]
    for k, v in rows:
        lines.append(f"| {k:<{col1}} | {v:<{col2}} |")
    lines.append(border)
    return "\n".join(lines)


def _show_summary(base: str, head: str, fmt: str) -> None:
    """Display project summary comparing ``base`` and ``head``.

    Args:
        base: Baseline git reference.
        head: Head git reference.
        fmt: Output format, ``"table"`` or ``"json"``.
    """

    cfg = load_config()
    version = read_project_version()
    old_api = build_api_at_ref(
        base, cfg.project.public_roots, cfg.ignore.paths, cfg.project.private_prefixes
    )
    new_api = build_api_at_ref(
        head, cfg.project.public_roots, cfg.ignore.paths, cfg.project.private_prefixes
    )
    impacts = diff_public_api(
        old_api,
        new_api,
        return_type_change=cfg.rules.return_type_change,
        param_annotation_change=cfg.rules.param_annotation_change,
    )
    if fmt == "json":
        logger.info(
            json.dumps(
                {
                    "version": version,
                    "public_symbols": sorted(new_api.keys()),
                    "changes": [i.__dict__ for i in impacts],
                },
                indent=2,
            )
        )
        return

    rows = [
        ("Version", version),
        ("Public symbols", str(len(new_api))),
        ("Changes since baseline", str(len(impacts))),
    ]
    logger.info("\n%s", _format_table(rows))
    if new_api:
        logger.info("Public symbols:")
        for sym in sorted(new_api):
            logger.info("  - %s", sym)
    if impacts:
        logger.info("Changes since baseline:")
        for imp in impacts:
            logger.info(
                "  - [%s] %s: %s",
                imp.severity.upper(),
                imp.symbol,
                imp.reason,
            )
    else:
        logger.info("No API-impacting changes since baseline.")


def init_command(args: argparse.Namespace) -> int:
    """Create an empty baseline release commit.

    This establishes a starting point for future semantic version bumps. The
    function is idempotent: if a baseline already exists, no new commit is
    created.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit status code. ``0`` indicates success or that the baseline was
        already present, while ``1`` indicates an error.

    Example:
        >>> init_command(argparse.Namespace(summary=None))  # doctest: +SKIP
        0
    """

    baseline = last_release_commit()
    if baseline is not None:
        logger.info("Baseline already initialised.")
        if getattr(args, "summary", None):
            _show_summary(baseline, "HEAD", args.summary)
        return 0

    try:
        run_git(
            [
                "commit",
                "--allow-empty",
                "-m",
                "chore(release): initialise baseline",
            ]
        )
    except GitCommandError as exc:  # pragma: no cover - git failure
        logger.error(format_git_error("Failed to create baseline commit", exc))
        return 1
    logger.info("Created baseline release commit.")
    if getattr(args, "summary", None):
        baseline = last_release_commit() or "HEAD"
        _show_summary(baseline, baseline, args.summary)
    return 0


__all__ = ["init_command"]
