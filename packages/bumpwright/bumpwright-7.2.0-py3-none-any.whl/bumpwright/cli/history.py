"""History command for the bumpwright CLI."""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any

from ..gitutils import last_release_commit, run_git
from ..versioning import read_project_version

logger = logging.getLogger(__name__)


def _commit_date(tag: str) -> str:
    """Return the commit date for ``tag``.

    Args:
        tag: Git tag whose commit date should be retrieved.

    Returns:
        The ISO-8601 commit timestamp associated with ``tag``. An empty string
        is returned if the lookup fails.
    """

    try:
        res = subprocess.run(
            ["git", "show", "-s", "--format=%cI", tag],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError:  # pragma: no cover - git failure
        return ""
    return res.stdout.strip()


def _diff_stats(prev: str, tag: str) -> tuple[int, int]:
    """Compute line change statistics between two tags.

    Args:
        prev: Previous tag in history.
        tag: Current tag for which statistics are computed.

    Returns:
        Tuple of ``(insertions, deletions)``.
    """

    res = subprocess.run(
        ["git", "diff", "--shortstat", prev, tag],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    out = res.stdout
    ins_match = re.search(r"(\d+) insertions?\(\+\)", out)
    del_match = re.search(r"(\d+) deletions?\(-\)", out)
    ins = int(ins_match.group(1)) if ins_match else 0
    dels = int(del_match.group(1)) if del_match else 0
    return ins, dels


def _rollback(tag: str, *, release: bool = True) -> int:
    """Remove ``tag`` and restore files changed in the tagged commit.

    Only files touched by the release commit are checked out from its parent so
    that untracked files remain untouched.

    Args:
        tag: Git tag identifying the release to undo.
        release: Whether to record the rollback as a release commit. When
            ``False``, the commit message omits the ``(release)`` marker so the
            repository no longer contains bumpwright release metadata.

    Returns:
        Status code where ``0`` indicates success and ``1`` signals an error.
    """

    try:
        commit = subprocess.run(
            ["git", "rev-list", "-n", "1", tag],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to resolve tag %s: %s", tag, exc)
        return 1

    try:
        run_git(["tag", "-d", tag])
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to delete tag %s: %s", tag, exc)
        return 1

    try:
        subprocess.run(["git", "revert", "--no-commit", commit], check=True)
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to revert %s: %s", tag, exc)
        return 1

    try:
        cfg = tomllib.loads(Path("bumpwright.toml").read_text(encoding="utf-8"))
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        changelog = None
    else:
        changelog = cfg.get("changelog", {}).get("path")
    if changelog:
        cp = Path(changelog)
        if cp.exists():
            try:
                run_git(["ls-files", "--error-unmatch", str(cp)])
            except subprocess.CalledProcessError:
                cp.unlink()

    try:
        status = run_git(["status", "--porcelain"]).stdout.strip()
        if status:
            msg = f"chore(release): undo {tag}" if release else f"chore: undo {tag}"
            run_git(["commit", "-am", msg])
    except subprocess.CalledProcessError as exc:
        logger.error("Failed to commit rollback for %s: %s", tag, exc)
        return 1

    return 0


def _purge() -> int:
    """Remove all bumpwright-generated release commits and tags.

    Tags whose associated commits begin with ``chore(release):`` are deleted and
    those commits are dropped from history while unrelated commits are
    preserved. After purging, the repository no longer contains bumpwright
    release metadata and must be reinitialised before further bumps.

    Returns:
        Exit status code where ``0`` indicates success and ``1`` signals an
        error.
    """

    try:
        res = subprocess.run(
            [
                "git",
                "for-each-ref",
                "refs/tags",
                "--format=%(refname:short) %(subject)",
            ],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - git failure
        logger.error("Failed to list tags: %s", exc)
        return 1

    for line in res.stdout.splitlines():
        tag, _, subject = line.partition(" ")
        if subject.startswith("chore(release):"):
            try:
                run_git(["tag", "-d", tag])
            except subprocess.CalledProcessError as exc:
                logger.error("Failed to delete tag %s: %s", tag, exc)
                return 1

    while True:
        commit = last_release_commit()
        if commit is None:
            break
        try:
            run_git(["rebase", "--onto", f"{commit}^", commit])
        except subprocess.CalledProcessError as exc:
            logger.error("Failed to drop release commit %s: %s", commit, exc)
            return 1

    try:
        cfg = tomllib.loads(Path("bumpwright.toml").read_text(encoding="utf-8"))
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        changelog = None
    else:
        changelog = cfg.get("changelog", {}).get("path")
    if changelog:
        cp = Path(changelog)
        if cp.exists():
            try:
                run_git(["ls-files", "--error-unmatch", str(cp)])
            except subprocess.CalledProcessError:
                cp.unlink()

    if last_release_commit() is None:
        logger.info("Removed bumpwright releases; project requires reinitialisation.")
        return 0

    logger.warning("Residual bumpwright release commits remain; manual cleanup needed.")
    return 1


def history_command(args: argparse.Namespace) -> int:
    """List git tags, roll back a tagged release, or purge bumpwright metadata.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit status code. ``0`` indicates success, while ``1`` signals an error
        interacting with git.

    Example:
        >>> history_command(argparse.Namespace(format="json", stats=False, rollback=None))  # doctest: +SKIP
        0
    """

    if getattr(args, "rollback", None):
        return _rollback(args.rollback)
    if getattr(args, "purge", False):
        return _purge()

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

    records: list[dict[str, Any]] = []
    for idx, tag in enumerate(tags):
        version = tag[1:] if tag.startswith("v") else tag
        date = _commit_date(tag)
        record: dict[str, Any] = {"tag": tag, "version": version, "date": date}
        if args.stats and idx < len(tags) - 1:
            prev = tags[idx + 1]
            ins, dels = _diff_stats(prev, tag)
            record["stats"] = {"insertions": ins, "deletions": dels}
        records.append(record)

    if args.format == "json":
        logger.info(json.dumps(records, indent=2))
    elif args.format == "md":
        header = ["Tag", "Version", "Date"]
        if args.stats:
            header.append("Stats")
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join("---" for _ in header) + " |",
        ]
        for rec in records:
            cols = [rec["tag"], rec["version"], rec["date"]]
            if args.stats:
                stats = rec.get("stats")
                cols.append(
                    f"+{stats['insertions']} -{stats['deletions']}" if stats else ""
                )
            lines.append("| " + " | ".join(cols) + " |")
        logger.info("\n".join(lines))
    else:
        for rec in records:
            line = f"{rec['tag']} {rec['version']} {rec['date']}"
            if args.stats:
                stats = rec.get("stats")
                if stats:
                    line += f" +{stats['insertions']} -{stats['deletions']}"
            logger.info(line)

    try:
        project_version = read_project_version()
    except Exception:  # pragma: no cover - missing file or field
        return 0

    latest = records[0]["version"]
    if project_version != latest:
        logger.warning(
            "Project version %s differs from latest tag %s",
            project_version,
            latest,
        )
    return 0
