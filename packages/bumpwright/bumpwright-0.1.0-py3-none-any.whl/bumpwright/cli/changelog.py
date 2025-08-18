"""Changelog utilities for the bumpwright CLI."""

from __future__ import annotations

import logging
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Template

from ..gitutils import (
    collect_commits,
    collect_contributors,
    last_release_commit,
    tag_for_commit,
)

logger = logging.getLogger(__name__)


def get_default_template() -> str:
    """Return the built-in changelog template text.

    Example:
        >>> 'Version' in get_default_template()
        True
    """

    template_path = (
        Path(__file__).resolve().parents[1] / "templates" / "changelog.md.j2"
    )
    return template_path.read_text(encoding="utf-8")


def _read_template(template_path: str | None) -> str:
    """Load a changelog template from ``template_path`` or return the default."""

    if template_path:
        return Path(template_path).read_text(encoding="utf-8")
    return get_default_template()


def _build_changelog(args: Any, new_version: str) -> str | None:
    """Generate changelog text based on CLI arguments.

    Args:
        args: Parsed command-line arguments containing changelog options.
        new_version: Version string for the upcoming release.

    Returns:
        Rendered changelog text or ``None`` when changelog emission is disabled
        or git metadata collection fails.
    """

    if getattr(args, "changelog", None) is None:
        return None

    base = last_release_commit() or f"{args.head}^"
    try:
        commits = collect_commits(base, args.head)
    except subprocess.CalledProcessError as exc:
        logger.warning("Failed to collect commits: %s", exc)
        return None
    prev_tag = tag_for_commit(base)
    patterns = [re.compile(p) for p in getattr(args, "changelog_exclude", [])]
    entries: list[dict[str, Any]] = []
    breaking: list[str] = []
    for sha, subject, body in commits:
        if any(p.search(subject) for p in patterns):
            continue
        link = None
        if getattr(args, "repo_url", None):
            base_url = args.repo_url.rstrip("/")
            link = f"{base_url}/commit/{sha}"
        entries.append({"sha": sha, "subject": subject, "link": link})
        if re.match(r"^[^:!]+(?:\([^)]*\))?!:", subject):
            breaking.append(subject)
        else:
            m = re.search(r"^BREAKING CHANGE:\s*(.+)", body, re.MULTILINE)
            if m:
                breaking.append(m.group(1).strip() or subject)

    try:
        contributors_raw = collect_contributors(base, args.head)
    except subprocess.CalledProcessError as exc:
        logger.warning("Failed to collect contributors: %s", exc)
        return None
    contributors: list[dict[str, str | None]] = []
    for name, email in contributors_raw:
        link = None
        if email.endswith("@users.noreply.github.com"):
            username = email.split("@", 1)[0].split("+")[-1]
            link = f"https://github.com/{username}"
        contributors.append({"name": name, "link": link})

    compare_url = None
    if getattr(args, "repo_url", None) and prev_tag:
        base_url = args.repo_url.rstrip("/")
        compare_url = f"{base_url}/compare/{prev_tag}...v{new_version}"

    now = datetime.now(timezone.utc)
    tmpl = Template(_read_template(getattr(args, "changelog_template", None)))
    rendered = tmpl.render(
        version=new_version,
        date=now.date().isoformat(),
        commits=entries,
        repo_url=getattr(args, "repo_url", None),
        release_datetime_iso=now.isoformat(),
        compare_url=compare_url,
        previous_tag=prev_tag,
        contributors=contributors,
        breaking_changes=breaking,
    )
    return rendered.rstrip() + "\n"
