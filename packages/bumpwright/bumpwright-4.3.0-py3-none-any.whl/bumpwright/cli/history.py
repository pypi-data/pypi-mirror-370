"""History command for the bumpwright CLI."""

from __future__ import annotations

import argparse
import logging
import subprocess

from ..versioning import read_project_version

logger = logging.getLogger(__name__)


def history_command(_args: argparse.Namespace) -> int:
    """List existing git tags and warn on version mismatches.

    Args:
        _args: Parsed command-line arguments. Present for API compatibility but
            currently unused.

    Returns:
        Exit status code. ``0`` indicates success, while ``1`` signals an error
        interacting with git.
    """

    try:
        res = subprocess.run(
            ["git", "tag", "--list", "--sort=-v:refname"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - git failure
        logger.error("Failed to list tags: %s", exc)
        return 1

    tags = [t for t in (line.strip() for line in res.stdout.splitlines()) if t]
    if not tags:
        logger.info("No tags found.")
        return 0

    for tag in tags:
        version = tag[1:] if tag.startswith("v") else tag
        logger.info("%s %s", tag, version)

    try:
        project_version = read_project_version()
    except Exception:  # pragma: no cover - missing file or field
        return 0

    latest = tags[0][1:] if tags[0].startswith("v") else tags[0]
    if project_version != latest:
        logger.warning(
            "Project version %s differs from latest tag %s",
            project_version,
            latest,
        )
    return 0
