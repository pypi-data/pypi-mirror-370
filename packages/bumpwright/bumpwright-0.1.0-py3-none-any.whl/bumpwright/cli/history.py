"""History command for the bumpwright CLI."""

from __future__ import annotations

import argparse
import json
import logging
import re
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

from ..gitutils import (
    GitCommandError,
    format_git_error,
    last_release_commit,
    run_git,
)
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
        res = run_git(["show", "-s", "--format=%cI", tag])
    except GitCommandError:  # pragma: no cover - git failure
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

    res = run_git(["diff", "--shortstat", prev, tag])
    out = res.stdout
    ins_match = re.search(r"(\d+) insertions?\(\+\)", out)
    del_match = re.search(r"(\d+) deletions?\(-\)", out)
    ins = int(ins_match.group(1)) if ins_match else 0
    dels = int(del_match.group(1)) if del_match else 0
    return ins, dels


def _rollback(tag: str, *, release: bool = True) -> int:
    """Remove ``tag`` and restore files changed in the tagged commit.

    Only files touched by the release commit are checked out from its parent so
    that untracked files remain untouched. The rollback aborts if uncommitted
    changes are present to avoid capturing unrelated modifications. Failed
    reverts are cleaned up via ``git revert --abort``.

    Args:
        tag: Git tag identifying the release to undo.
        release: Whether to record the rollback as a release commit. When
            ``False``, the commit message omits the ``(release)`` marker so the
            repository no longer contains bumpwright release metadata.

    Returns:
        Status code where ``0`` indicates success and ``1`` signals an error.
    """

    try:
        commit = run_git(["rev-list", "-n", "1", tag]).stdout.strip()
    except GitCommandError as exc:
        logger.error(format_git_error(f"Failed to resolve tag {tag}", exc))
        return 1

    try:
        status = run_git(["status", "--porcelain"]).stdout.strip()
        if status:
            raise RuntimeError("Uncommitted changes present; aborting rollback")
    except (GitCommandError, RuntimeError) as exc:
        if isinstance(exc, GitCommandError):
            logger.error(format_git_error("Failed to check worktree state", exc))
        else:
            logger.error(str(exc))
        return 1

    try:
        run_git(["tag", "-d", tag])
    except GitCommandError as exc:
        logger.error(format_git_error(f"Failed to delete tag {tag}", exc))
        return 1

    try:
        run_git(["revert", "--no-commit", commit])
    except GitCommandError as exc:
        logger.error(format_git_error(f"Failed to revert {tag}", exc))
        try:
            run_git(["revert", "--abort"])
        except GitCommandError:
            pass
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
            except GitCommandError:
                cp.unlink()

    try:
        status = run_git(["status", "--porcelain"]).stdout.strip()
        if status:
            msg = f"chore(release): undo {tag}" if release else f"chore: undo {tag}"
            run_git(["commit", "-m", msg])
    except GitCommandError as exc:
        logger.error(format_git_error(f"Failed to commit rollback for {tag}", exc))
        return 1

    return 0


def _purge() -> int:
    """Remove all bumpwright-generated release commits and tags.

    Tags whose associated commits begin with ``chore(release):`` are deleted and
    those commits are dropped from history while unrelated commits are
    preserved. The purge requires a clean working tree and aborts ongoing rebases
    when conflicts occur. After purging, the repository no longer contains
    bumpwright release metadata and must be reinitialised before further bumps.

    Returns:
        Exit status code where ``0`` indicates success and ``1`` signals an
        error.
    """

    try:
        status = run_git(["status", "--porcelain"]).stdout.strip()
        if status:
            raise RuntimeError("Uncommitted changes present; aborting purge")
    except (GitCommandError, RuntimeError) as exc:
        if isinstance(exc, GitCommandError):
            logger.error(format_git_error("Failed to check worktree state", exc))
        else:
            logger.error(str(exc))
        return 1

    try:
        res = run_git(
            [
                "for-each-ref",
                "refs/tags",
                "--format=%(refname:short) %(subject)",
            ]
        )
    except GitCommandError as exc:  # pragma: no cover - git failure
        logger.error(format_git_error("Failed to list tags", exc))
        return 1

    for line in res.stdout.splitlines():
        tag, _, subject = line.partition(" ")
        if subject.startswith("chore(release):"):
            try:
                run_git(["tag", "-d", tag])
            except GitCommandError as exc:
                logger.error(format_git_error(f"Failed to delete tag {tag}", exc))
                return 1

    while True:
        commit = last_release_commit()
        if commit is None:
            break
        try:
            run_git(["rebase", "--onto", f"{commit}^", commit])
        except GitCommandError as exc:
            logger.error(
                format_git_error(f"Failed to drop release commit {commit}", exc)
            )
            try:
                run_git(["rebase", "--abort"])
            except GitCommandError:
                pass
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
            except GitCommandError:
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
        res = run_git(["tag", "--list", "--sort=-v:refname"])
    except GitCommandError as exc:  # pragma: no cover - git failure
        logger.error(format_git_error("Failed to list tags", exc))
        return 1

    tags = [t for t in (line.strip() for line in res.stdout.splitlines()) if t]
    if not tags:
        logger.info("No tags found.")
        return 0

    records: list[dict[str, Any]] = []
    for idx, tag in enumerate(tags):
        version = tag[1:] if tag.startswith("v") else tag
        date_iso = _commit_date(tag)
        if args.local_time and date_iso:
            dt = datetime.fromisoformat(date_iso).astimezone()
            date = dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            date = date_iso
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
