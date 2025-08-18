"""Lightweight wrappers around git for file inspection and metadata.

These utilities abstract common git operations used throughout bumpwright. The
functions favour simplicity and returning structured Python data rather than raw
subprocess output.

Example:
    >>> 'pyproject.toml' in changed_paths('HEAD^', 'HEAD')
    True
"""

from __future__ import annotations

import logging
import re
import subprocess
from collections.abc import Iterable
from fnmatch import fnmatch
from functools import lru_cache
from io import BytesIO
from pathlib import Path

# Matches ``git shortlog -sne`` lines ``"<count> <name> <email>"``.
CONTRIB_RE = re.compile(r"\s*\d+\s+(.+)\s+<([^>]+)>")

logger = logging.getLogger(__name__)


def _run(cmd: list[str], cwd: str | None = None) -> str:
    """Run a subprocess command and return its ``stdout``.

    This tiny helper keeps command execution consistent across the module and
    surfaces git failures immediately, which makes debugging far less painful.

    Args:
        cmd: Command and arguments to execute.
        cwd: Directory in which to run the command.

    Returns:
        Captured standard output from the command.

    Raises:
        subprocess.CalledProcessError: If the command exits with a non-zero
            status.
    """

    res = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return res.stdout


class GitCommandError(subprocess.CalledProcessError):
    """Raised when a git command exits with a non-zero status."""


def format_git_error(msg: str, exc: "GitCommandError") -> str:
    """Format a git error message for logging.

    Args:
        msg: Contextual message describing the failure.
        exc: The underlying :class:`GitCommandError` instance.

    Returns:
        A concise string combining the context and git's stderr output.
    """

    detail = (exc.stderr or exc.output or "").strip()
    return f"{msg}: {detail}" if detail else f"{msg}: {exc}"


def run_git(
    args: list[str], cwd: str | None = None
) -> subprocess.CompletedProcess[str]:
    """Run a git command and capture its output.

    The wrapper ensures we interact with git in a uniform fashion, making it
    easier to spot errors and reason about command execution in higher-level
    functions.

    Args:
        args: Git command arguments excluding the leading ``git``.
        cwd: Working directory in which to run the command.

    Returns:
        The completed process with both ``stdout`` and ``stderr`` captured as
        strings.

    Raises:
        GitCommandError: If git returns a non-zero status.
    """

    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:  # pragma: no cover - error path
        raise GitCommandError(
            exc.returncode,
            exc.cmd,
            output=exc.stdout,
            stderr=exc.stderr,
        ) from exc


def changed_paths(base: str, head: str, cwd: str | None = None) -> set[str]:
    """Return paths changed between two git references.

    It offers a quick way to determine which files differ, helping higher-level
    logic decide what needs to be inspected or ignored during a bump.

    Args:
        base: Base git reference.
        head: Head git reference.
        cwd: Repository path.

    Returns:
        Set of file paths that differ between the two refs.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.

    Example:
        >>> sorted(changed_paths('HEAD^', 'HEAD'))
        ['README.md', 'bumpwright/gitutils.py']
    """

    out = _run(["git", "diff", "--name-only", f"{base}..{head}"], cwd)
    return {line.strip() for line in out.splitlines() if line.strip()}


@lru_cache(maxsize=None)
def _list_py_files_at_ref_cached(
    ref: str,
    roots: tuple[str, ...],
    ignore_globs: tuple[str, ...],
    cwd: str | None,
) -> frozenset[str]:
    """Return cached Python file paths for a given ref.

    It shells out to ``git ls-tree`` and filters for ``.py`` files, caching the
    result so repeated checks remain snappy even on large repositories.

    Args:
        ref: Git reference to inspect.
        roots: Root directories to include.
        ignore_globs: Glob patterns to exclude.
        cwd: Repository path.

    Returns:
        Frozen set of matching Python file paths.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.
    """

    out = _run(["git", "ls-tree", "-r", "--name-only", ref], cwd)
    paths: set[str] = set()
    roots_norm = [str(Path(r)) for r in roots]
    for line in out.splitlines():
        if not line.endswith(".py"):
            continue
        p = Path(line)
        if any(
            str(p).startswith(r.rstrip("/") + "/") or str(p) == r for r in roots_norm
        ):
            s = str(p)
            if ignore_globs and any(fnmatch(s, pat) for pat in ignore_globs):
                continue
            paths.add(s)
    return frozenset(paths)


def list_py_files_at_ref(
    ref: str,
    roots: Iterable[str],
    ignore_globs: Iterable[str] | None = None,
    cwd: str | None = None,
) -> set[str]:
    """List Python files under given roots at a git ref.

    The function leans on :func:`_list_py_files_at_ref_cached` for the heavy
    lifting, so repeat queries avoid redundant git calls and stay quick.

    Results are cached per ``(ref, tuple(roots), tuple(ignores))`` for improved
    performance. Use ``list_py_files_at_ref.cache_clear()`` to invalidate.

    Args:
        ref: Git reference to inspect.
        roots: Root directories to include.
        ignore_globs: Optional glob patterns to exclude.
        cwd: Repository path.

    Returns:
        Set of matching Python file paths.

    Raises:
        subprocess.CalledProcessError: If the underlying git command fails.

    Example:
        >>> sorted(list_py_files_at_ref('HEAD', ['bumpwright']))[:2]
        ['bumpwright/__init__.py', 'bumpwright/cli/__init__.py']
    """

    roots_tuple = tuple(roots)
    ignores_tuple = tuple(ignore_globs or ())
    return set(_list_py_files_at_ref_cached(ref, roots_tuple, ignores_tuple, cwd))


list_py_files_at_ref.cache_clear = _list_py_files_at_ref_cached.cache_clear  # type: ignore[attr-defined]


def read_file_at_ref(ref: str, path: str, cwd: str | None = None) -> str | None:
    """Read the contents of ``path`` at ``ref`` if it exists.

    This is a thin wrapper around :func:`read_files_at_ref` that retrieves a
    single file. Results are cached via ``read_files_at_ref``; call
    ``read_file_at_ref.cache_clear()`` to invalidate. Using git rather than the
    working tree lets us inspect historic states without checking out branches.

    Args:
        ref: Git reference at which to read the file.
        path: File path relative to the repository root.
        cwd: Repository path.

    Returns:
        File contents, or ``None`` if the file does not exist at ``ref``.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.

    Example:
        >>> read_file_at_ref('HEAD', 'README.md')[:7]
        '# bump'
    """

    return read_files_at_ref(ref, [path], cwd).get(path)


@lru_cache(maxsize=None)
def _read_files_at_ref_cached(
    ref: str, paths: tuple[str, ...], cwd: str | None
) -> dict[str, str | None]:
    """Return cached contents for multiple paths at a git reference.

    The function batches ``git cat-file`` calls, which is markedly faster than
    spawning git for each file. The results are cached for subsequent requests to
    spare the filesystem.

    Args:
        ref: Git reference at which to read files.
        paths: Iterable of file paths relative to the repository root.
        cwd: Repository path.

    Returns:
        Mapping of file paths to their contents or ``None`` if a file does not
        exist at ``ref``.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.
    """

    if not paths:
        return {}
    spec = "\n".join(f"{ref}:{p}" for p in paths) + "\n"
    res = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=cwd,
        input=spec.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if res.returncode != 0:
        raise subprocess.CalledProcessError(
            res.returncode,
            "git cat-file --batch",
            output=res.stdout.decode(),
            stderr=res.stderr.decode(),
        )

    out = BytesIO(res.stdout)
    results: dict[str, str | None] = {}
    for path in paths:
        header = out.readline().decode().strip()
        if not header:
            results[path] = None
            continue
        if header.endswith(" missing"):
            results[path] = None
            continue
        _sha, _typ, size_str = header.split()
        size = int(size_str)
        content = out.read(size).decode()
        out.read(1)
        results[path] = content
    return results


def read_files_at_ref(
    ref: str, paths: Iterable[str], cwd: str | None = None
) -> dict[str, str | None]:
    """Read multiple file contents at ``ref`` in a single subprocess call.

    By delegating to :func:`_read_files_at_ref_cached`, the function avoids
    running multiple git commands and keeps results cached for reuse.

    Results are cached per ``(ref, tuple(paths), cwd)`` for improved
    performance. Use ``read_files_at_ref.cache_clear()`` to invalidate.

    Args:
        ref: Git reference at which to read files.
        paths: Iterable of file paths relative to the repository root.
        cwd: Repository path.

    Returns:
        Mapping of file paths to their contents or ``None`` if a file does not
        exist at ``ref``.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.
    """

    paths_tuple = tuple(paths)
    return dict(_read_files_at_ref_cached(ref, paths_tuple, cwd))


read_files_at_ref.cache_clear = _read_files_at_ref_cached.cache_clear  # type: ignore[attr-defined]


read_file_at_ref.cache_clear = read_files_at_ref.cache_clear  # type: ignore[attr-defined]


def last_release_commit(cwd: str | None = None) -> str | None:
    """Return the most recent release commit created by bumpwright.

    It scans the log for commits with the conventional ``chore(release):``
    prefix, which bumpwright itself writes when publishing. This helps commands
    like ``history`` start from the last release.

    Args:
        cwd: Repository path to inspect.

    Returns:
        Hash of the latest ``chore(release):`` commit or ``None`` if not found.

    Raises:
        None
    """

    try:
        out = _run(
            ["git", "log", "-n", "1", "--grep", "^chore(release):", "--format=%H"],
            cwd,
        )
    except subprocess.CalledProcessError:
        return None
    return out.strip() or None


def collect_commits(
    base: str, head: str, cwd: str | None = None
) -> list[tuple[str, str, str]]:
    """Collect commit metadata between two references.

    It returns short hashes along with the subject and body, giving callers a
    simple way to display history or craft changelog entries.

    Args:
        base: Older git reference (exclusive).
        head: Newer git reference (inclusive).
        cwd: Optional repository path.

    Returns:
        List of ``(short_sha, subject, body)`` tuples ordered newest first.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.

    Example:
        >>> sha, subject, _ = collect_commits('HEAD^', 'HEAD')[0]
        >>> len(sha) == 7 and bool(subject)
        True
    """

    out = _run(["git", "log", "--format=%h%x00%s%x00%b%x00", f"{base}..{head}"], cwd)
    parts = out.split("\0")
    commits: list[tuple[str, str, str]] = []
    for i in range(0, len(parts) - 1, 3):
        sha, subject, body = parts[i], parts[i + 1], parts[i + 2]
        if not sha:
            continue
        commits.append((sha, subject, body.rstrip()))
    return commits


def commit_message(ref: str, cwd: str | None = None) -> str:
    """Return the full commit message for ``ref``.

    It is handy when generating changelog entries or for debugging, as the
    output mirrors what ``git show`` would print for a single commit.

    Args:
        ref: Git reference to inspect.
        cwd: Repository path.

    Returns:
        Commit message including subject and body.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.
    """

    return _run(["git", "show", "-s", "--format=%B", ref], cwd)


def commit_iso_datetime(ref: str, cwd: str | None = None) -> str:
    """Return the ISO-8601 commit timestamp for ``ref``.

    The timestamp is useful for audit trails or for presenting release histories
    in chronological order regardless of locale settings.

    Args:
        ref: Git reference to inspect.
        cwd: Repository path.

    Returns:
        ISO-8601 formatted commit timestamp.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.
    """

    out = _run(["git", "show", "-s", "--format=%cI", ref], cwd)
    return out.strip()


def tag_for_commit(commit: str, cwd: str | None = None) -> str | None:
    """Return the first tag pointing at ``commit`` if present.

    When multiple tags exist, the function simply returns the first one, which is
    enough for identifying releases in typical workflows.

    Args:
        commit: Commit hash to inspect.
        cwd: Repository path.

    Returns:
        Tag name pointing at ``commit`` or ``None`` if no tag exists.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.
    """

    out = _run(["git", "tag", "--points-at", commit], cwd)
    return out.splitlines()[0].strip() if out.strip() else None


def collect_contributors(
    base: str, head: str, cwd: str | None = None
) -> list[tuple[str, str]]:
    """Return contributors between two references.

    It parses ``git shortlog`` output to produce a simple list of names and
    emails, which can be handy for acknowledgements or release notes.

    Args:
        base: Older git reference (exclusive).
        head: Newer git reference (inclusive).
        cwd: Optional repository path.

    Returns:
        List of ``(name, email)`` tuples.

    Raises:
        subprocess.CalledProcessError: If the git invocation fails.
    """

    out = _run(["git", "shortlog", "-sne", f"{base}..{head}"], cwd)
    contributors: list[tuple[str, str]] = []
    for line in out.splitlines():
        match = CONTRIB_RE.match(line)
        if match:
            contributors.append((match.group(1).strip(), match.group(2).strip()))
    return contributors


def fetch_tags(cwd: str | None = None) -> None:
    """Fetch tags from the default remote, ignoring failures.

    Fetching tags keeps the local repository in sync with remote releases.
    Errors are suppressed because some repositories may lack a remote or have
    restricted network access.

    Args:
        cwd: Optional path of the repository in which to run ``git fetch``.
    """

    try:
        run_git(["fetch", "--tags"], cwd=cwd)
    except subprocess.CalledProcessError as exc:  # pragma: no cover - fetch failure
        logger.debug("Skipping tag fetch: %s", exc)
