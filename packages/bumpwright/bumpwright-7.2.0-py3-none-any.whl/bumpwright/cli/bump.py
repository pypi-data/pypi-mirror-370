"""Version bump command for the bumpwright CLI."""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable

from ..compare import Decision
from ..config import Config, load_config
from ..gitutils import changed_paths, last_release_commit, run_git
from ..versioning import VersionChange, apply_bump, find_pyproject
from .changelog import _build_changelog
from .decide import _infer_level

logger = logging.getLogger(__name__)


class GitDiffError(RuntimeError):
    """Raised when git diff cannot determine changed paths.

    This typically occurs when one of the provided references does not exist or
    the repository lacks sufficient history to perform the comparison.

    Args:
        base: Base git reference for the diff.
        head: Head git reference for the diff.
    """

    def __init__(self, base: str, head: str) -> None:
        super().__init__(
            f"Cannot determine changes between {base} and {head}. Ensure both refs exist and share history."
        )


def _commit_tag(
    files: Iterable[str | Path], version: str, commit: bool, tag: bool
) -> int:
    """Optionally commit and tag the updated version.

    Args:
        files: Paths of files to stage before committing.
        version: Version string to commit and tag.
        commit: Whether to create a commit.
        tag: Whether to create a git tag.

    Returns:
        ``0`` on success and ``1`` if any git operation fails.

    Raises:
        RuntimeError: If the requested tag already exists.
    """

    if not (commit or tag):
        return 0

    if tag:
        # Abort early if the tag already exists to avoid accidental reuse.
        result = subprocess.run(
            ["git", "rev-parse", "--verify", f"v{version}"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            msg = f"Tag v{version} already exists. Delete the tag manually or use a different version."
            raise RuntimeError(msg)

    try:
        if commit:
            for file in files:
                run_git(["add", str(file)])
            run_git(["commit", "-m", f"chore(release): {version}"])
        if tag:
            run_git(["tag", f"v{version}"])
    except (
        subprocess.CalledProcessError
    ) as exc:  # pragma: no cover - simulated in tests
        if commit and "commit" in exc.cmd:
            logger.error("Failed to commit release %s: %s", version, exc)
        else:
            logger.error("Failed to create tag v%s: %s", version, exc)
        return 1
    return 0


def _resolve_pyproject(path: str) -> Path:
    """Locate ``pyproject.toml`` relative to ``path``."""

    candidate = Path(path)
    if candidate.is_file():
        return candidate
    if candidate.name == "pyproject.toml":
        found = find_pyproject()
        if found:
            return found
    raise FileNotFoundError(f"pyproject.toml not found at {path}")


def _resolve_refs(args: argparse.Namespace) -> tuple[str, str]:
    """Determine base and head git references.

    Args:
        args: Parsed command-line arguments containing ``base`` and ``head``.

    Returns:
        Tuple of base and head git references.
    """

    if args.base:
        base = args.base
    else:
        base = last_release_commit() or "HEAD^"
    return base, args.head


def _safe_changed_paths(base: str, head: str) -> set[str]:
    """Return changed paths or raise :class:`GitDiffError` on failure.

    Args:
        base: Base git reference for comparison.
        head: Head git reference for comparison.

    Returns:
        Set of paths changed between ``base`` and ``head``.

    Raises:
        GitDiffError: If the diff between ``base`` and ``head`` cannot be
            computed.
    """

    try:
        return changed_paths(base, head)
    except (
        subprocess.CalledProcessError
    ) as exc:  # pragma: no cover - exercised in tests
        raise GitDiffError(base, head) from exc


def _matches_version_path(path: str, patterns: Iterable[str]) -> bool:
    """Check whether ``path`` matches any version file pattern.

    Args:
        path: File path relative to the repository root.
        patterns: Glob patterns representing version file locations.

    Returns:
        bool: ``True`` if the path represents a version file.

    Notes:
        ``__init__.py`` files are treated as version files only when they
        contain a ``__version__`` assignment. This prevents regular package
        modules from being ignored during bump detection.
    """

    abs_path = str(Path(path).resolve())
    for pat in patterns:
        if fnmatch(path, pat) or fnmatch(abs_path, pat):
            if Path(path).name == "__init__.py":
                try:
                    # Only classify as a version file if it actually defines
                    # ``__version__``. Otherwise, treat the change as a normal
                    # source modification.
                    if "__version__" not in Path(path).read_text(encoding="utf-8"):
                        continue
                except OSError:
                    # If the file cannot be read, conservatively treat it as a
                    # version file to avoid false positives.
                    pass
            return True
    return False


def _prepare_version_files(
    cfg: Config,
    args: argparse.Namespace,
    pyproject: Path,
    base: str,
    head: str,
) -> list[str] | None:
    """Build version file list and decide if a bump is necessary.

    Args:
        cfg: Project configuration object.
        args: Parsed command line arguments.
        pyproject: Path to the canonical ``pyproject.toml`` file.
        base: Git reference representing the comparison base.
        head: Git reference representing the comparison head.

    Returns:
        List of file patterns to update, or ``None`` when no bump is required.
    """

    paths = list(cfg.version.paths)
    if args.version_path:
        paths.extend(args.version_path)
    changed = _safe_changed_paths(base, head)
    filtered = {
        p
        for p in changed
        if p != pyproject.name and not _matches_version_path(p, paths)
    }
    if not filtered:
        return None
    return paths


def _display_result(
    args: argparse.Namespace, vc: VersionChange, decision: Decision
) -> None:
    """Show bump outcome using the selected format."""

    if args.format == "json":
        logger.info(
            json.dumps(
                {
                    "old_version": vc.old,
                    "new_version": vc.new,
                    "level": vc.level,
                    "confidence": decision.confidence,
                    "reasons": decision.reasons,
                    "files": [str(p) for p in vc.files],
                    "skipped": [str(p) for p in vc.skipped],
                },
                indent=2,
            )
        )
    elif args.format == "md":
        logger.info("Bumped version: `%s` -> `%s` (%s)", vc.old, vc.new, vc.level)
        logger.info(
            "Updated files:\n%s",
            "\n".join(f"- `{p}`" for p in vc.files),
        )
        if vc.skipped:
            logger.info(
                "Skipped files:\n%s",
                "\n".join(f"- `{p}`" for p in vc.skipped),
            )
    else:
        logger.info("Bumped version: %s -> %s (%s)", vc.old, vc.new, vc.level)
        logger.info("Updated files: %s", ", ".join(str(p) for p in vc.files))
        if vc.skipped:
            logger.info("Skipped files: %s", ", ".join(str(p) for p in vc.skipped))


def _write_changelog(args: argparse.Namespace, changelog: str | None) -> None:
    """Persist changelog content based on user options."""

    if changelog is None:
        return
    if args.changelog == "-":
        logger.info("%s", changelog.rstrip())
    else:
        with open(args.changelog, "a", encoding="utf-8") as fh:
            fh.write(changelog)


def bump_command(args: argparse.Namespace) -> int:
    """Apply a version bump based on repository changes.

    Args:
        args: Parsed command-line arguments with fields corresponding to CLI
            options. Important attributes include:

            config (str): Path to configuration file. Defaults to
                ``bumpwright.toml``.

            base (str | None): Git reference used as the comparison base when
                inferring the bump level. Defaults to the last release commit or
                ``HEAD^``.

            head (str): Git reference representing the working tree. Defaults to
                ``HEAD``.

            format (str): Output format, one of ``text`` (default), ``md``, or
                ``json``.

            repo_url (str | None): Base repository URL for generating commit
                links in Markdown output.

            enable_analyser (list[str]): Names of analysers to enable in
                addition to configuration.

            disable_analyser (list[str]): Names of analysers to disable even if
                configured.

            pyproject (str): Path to ``pyproject.toml``. Defaults to
                ``pyproject.toml``.

            version_path (list[str]): Extra glob patterns for files whose
                version fields should be updated. Defaults include
                ``pyproject.toml``, ``setup.py``, ``setup.cfg``, and any
                ``__init__.py``, ``version.py``, or ``_version.py`` files.

            version_ignore (list[str]): Glob patterns for paths to exclude from
                version updates.

            commit (bool): Create a git commit containing the version change.

            tag (bool): Create a git tag for the new version.

            dry_run (bool): Show the new version without modifying files.

            changelog (str | None): Write release notes to the given file or
                stdout when ``-`` is provided.

            changelog_template (str | None): Path to a Jinja2 template used to
                render changelog entries. Defaults to the built-in template.

            changelog_exclude (list[str]): Regex patterns of commit subjects to
                exclude from changelog entries.

    Returns:
        Exit status code. ``0`` indicates success; ``1`` indicates an error.
    """

    cfg: Config = load_config(args.config)
    if args.changelog is None and cfg.changelog.path:
        args.changelog = cfg.changelog.path
    if getattr(args, "changelog_template", None) is None and cfg.changelog.template:
        args.changelog_template = cfg.changelog.template
    if getattr(args, "repo_url", None) is None and cfg.changelog.repo_url:
        args.repo_url = cfg.changelog.repo_url
    excludes = list(cfg.changelog.exclude)
    cli_excludes = getattr(args, "changelog_exclude", []) or []
    excludes.extend(cli_excludes)
    args.changelog_exclude = excludes

    decision: Decision | None = None
    base, head = _resolve_refs(args)

    try:
        pyproject = _resolve_pyproject(args.pyproject)
        paths = _prepare_version_files(cfg, args, pyproject, base, head)
    except (FileNotFoundError, GitDiffError) as exc:
        logger.error("Error: %s", exc)
        return 1
    if paths is None:
        logger.info("No version bump needed")
        return 0

    decision = _infer_level(base, head, cfg, args)
    if decision.level is None:
        logger.info("No version bump needed")
        return 0
    level = decision.level

    if (args.commit or args.tag) and not args.dry_run:
        status: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        )
        if status.stdout.strip():
            logger.error("Error: working directory has uncommitted changes")
            return 1

    ignore = list(cfg.version.ignore)
    if args.version_ignore:
        ignore.extend(args.version_ignore)
    vc = apply_bump(
        level,
        pyproject_path=pyproject,
        dry_run=args.dry_run,
        paths=paths,
        ignore=ignore,
        cfg=cfg,
    )
    changelog = _build_changelog(args, vc.new)
    _display_result(args, vc, decision)
    if not args.dry_run:
        if _commit_tag(vc.files, vc.new, args.commit, args.tag):
            return 1
    _write_changelog(args, changelog)
    return 0
