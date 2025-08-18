"""Utilities to read and bump project version numbers."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from fnmatch import fnmatch
from functools import cache, lru_cache
from glob import glob
from pathlib import Path

from tomlkit import dumps as toml_dumps
from tomlkit import parse as toml_parse

from .config import Config, load_config
from .types import BumpLevel
from .version_schemes import get_version_scheme

# Precompiled regex patterns for locating version assignments. The second
# capture group extracts the existing version string for comparison.
_VERSION_RE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(__version__\s*=\s*['\"])([^'\"]+)(['\"])"),
    re.compile(r"(VERSION\s*=\s*['\"])([^'\"]+)(['\"])"),
    re.compile(r"(version\s*=\s*['\"])([^'\"]+)(['\"])"),
]


@cache
def _get_default_config() -> Config:
    """Return cached configuration loading from disk on first use.

    The helper means we only hit the filesystem once during a run, keeping
    configuration lookups speedy and predictable.

    Returns:
        Loaded :class:`~bumpwright.config.Config` instance.

    Raises:
        None
    """

    return load_config()


@dataclass
class VersionChange:
    """Result of applying a version bump.

    Attributes:
        old: Previous version string.
        new: New version string after bump.
        level: Bump level applied (``"major"``, ``"minor"``, ``"patch"``,
            ``"pre"``, or ``"build"``).
        files: Files updated with the new version.
        skipped: Files where the old version string was not found.
    """

    old: str
    new: str
    level: BumpLevel
    files: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)


def bump_string(v: str, level: BumpLevel, scheme: str | None = None) -> str:
    """Increment ``v`` according to ``level`` using a version scheme.

    Delegating to the configured scheme keeps version logic centralised, so
    projects can swap strategies without altering their tooling.

    Args:
        v: Version string to bump.
        level: Desired bump level.
        scheme: Optional scheme name. When ``None``, the configured scheme from
            ``bumpwright.toml`` is used.

    Returns:
        Bumped version string.

    Raises:
        ValueError: If ``level`` or the scheme name is unsupported.

    Example:
        >>> bump_string('1.2.3', 'patch')
        '1.2.4'
    """

    scheme_name = scheme or _get_default_config().version.scheme
    impl = get_version_scheme(scheme_name)
    return impl.bump(v, level)


def find_pyproject(start: str | Path | None = None) -> Path | None:
    """Search upward from ``start`` for ``pyproject.toml``.

    Walking upwards allows commands to run from subdirectories without extra
    configuration, mirroring how tools like ``git`` behave.

    Args:
        start: Directory to begin searching from. Defaults to the current working
            directory.

    Returns:
        Path to the discovered ``pyproject.toml`` file, or ``None`` if not found.

    Raises:
        None
    """

    path = Path(start or Path.cwd()).resolve()
    for parent in [path, *path.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def read_project_version(pyproject_path: str | Path = "pyproject.toml") -> str:
    """Read the project version from a ``pyproject.toml`` file.

    The function tolerates being called from subdirectories by looking for the
    nearest ``pyproject.toml`` upwards if the provided path does not exist.

    Args:
        pyproject_path: Path to the ``pyproject.toml`` file.

    Returns:
        Project version string.

    Raises:
        FileNotFoundError: If the file cannot be located.
        KeyError: If the version field is missing.
    """

    p = Path(pyproject_path)
    if not p.is_file():
        p = find_pyproject(p.parent)
        if p is None:
            raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")
    data = toml_parse(p.read_text(encoding="utf-8"))
    try:
        return str(data["project"]["version"])
    except Exception as e:  # pragma: no cover - explicit re-raise for clarity
        raise KeyError("project.version not found in pyproject.toml") from e


def write_project_version(
    new_version: str, pyproject_path: str | Path = "pyproject.toml"
) -> None:
    """Write ``new_version`` to the ``pyproject.toml`` file.

    If the supplied path is missing, the nearest ``pyproject.toml`` is located
    automatically, mirroring :func:`read_project_version`.

    Args:
        new_version: Version string to write.
        pyproject_path: Path to the ``pyproject.toml`` file.

    Raises:
        FileNotFoundError: If the file cannot be located.
        KeyError: If the ``[project]`` table is missing from the file.
    """

    p = Path(pyproject_path)
    if not p.is_file():
        p = find_pyproject(p.parent)
        if p is None:
            raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")
    data = toml_parse(p.read_text(encoding="utf-8"))
    if "project" not in data:
        raise KeyError("No [project] table in pyproject.toml")
    data["project"]["version"] = new_version
    p.write_text(toml_dumps(data), encoding="utf-8")


def clear_version_file_cache() -> None:
    """Clear cached version file resolutions.

    This is a simple escape hatch when the set of files containing version
    strings changes during runtime.

    Raises:
        None
    """

    _resolve_files_cached.cache_clear()


def apply_bump(  # noqa: PLR0913
    level: BumpLevel,
    pyproject_path: str | Path = "pyproject.toml",
    dry_run: bool = False,
    paths: Iterable[str] | None = None,
    ignore: Iterable[str] | None = None,
    scheme: str | None = None,
    cfg: Config | None = None,
    config_path: str | Path | None = None,
) -> VersionChange:
    """Apply a version bump and update version strings.

    The function ties together reading the current version, computing the bump,
    writing the new value, and updating any additional files that reference it.

    Args:
        level: Bump level to apply.
        pyproject_path: Path to the canonical ``pyproject.toml`` file.
        dry_run: If ``True``, compute the new version without writing to disk.
        paths: Glob patterns pointing to files that may contain the version.
            Defaults include ``pyproject.toml``, ``setup.py``, ``setup.cfg`` and
            any ``__init__.py``, ``version.py`` or ``_version.py`` files within
            the project. Custom patterns extend this list.
        ignore: Glob patterns to exclude from ``paths``. Defaults to values from
            the project configuration when ``None``.
        scheme: Versioning scheme identifier. When ``None``, the scheme from
            configuration is used.
        cfg: Pre-loaded configuration object. When provided, ``config_path`` is
            ignored.
        config_path: Location of the configuration file to load when ``cfg`` is
            ``None``. Defaults to ``"bumpwright.toml"``.

    Returns:
        :class:`VersionChange` detailing the old and new versions, updated files,
        and any files skipped due to mismatched versions.

    Raises:
        FileNotFoundError: If the project metadata file cannot be found.
        KeyError: If required version information is missing.
        ValueError: If the bump level or scheme is unsupported.

    Notes:
        The most recent file resolution is cached based on ``paths`` and
        ``ignore`` patterns. Call :func:`clear_version_file_cache` if the
        filesystem changes and a fresh resolution is required.

    Example:
        >>> apply_bump('patch', dry_run=True).new  # doctest: +SKIP
        '6.0.1'
    """

    cfg = cfg or load_config(config_path or "bumpwright.toml")
    if paths is None:
        paths = cfg.version.paths
    if ignore is None:
        ignore = cfg.version.ignore
    if scheme is None:
        scheme = cfg.version.scheme

    paths_t = tuple(paths)
    ignore_t = tuple(ignore)
    old = read_project_version(pyproject_path)
    new = bump_string(old, level, scheme)
    if dry_run:
        return VersionChange(old=old, new=new, level=level)

    write_project_version(new, pyproject_path)
    updated, skipped = _update_additional_files(
        new, old, paths_t, ignore_t, pyproject_path
    )
    return VersionChange(
        old=old,
        new=new,
        level=level,
        files=[Path(pyproject_path), *updated],
        skipped=skipped,
    )


def _update_additional_files(
    new: str,
    old: str,
    patterns: Iterable[str],
    ignore: Iterable[str],
    pyproject_path: str | Path,
) -> tuple[list[Path], list[Path]]:
    """Update version strings in files matching ``patterns``.

    Each candidate file is examined and, if it contains the old version string,
    rewritten in place with the new one.

    Args:
        new: New version string.
        old: Previous version string.
        patterns: Glob patterns to search for files.
        ignore: Glob patterns to skip.
        pyproject_path: Canonical ``pyproject.toml`` path to skip (already updated).

    Returns:
        Tuple of lists: files updated and files skipped due to version mismatch.

    Raises:
        OSError: If reading or writing any file fails.
    """

    base = Path(pyproject_path).resolve().parent
    files = _resolve_files(patterns, ignore, base)
    canon = Path(pyproject_path).resolve()
    changed: list[Path] = []
    skipped: list[Path] = []
    for f in files:
        if f.resolve() == canon:
            continue
        if _replace_version(f, old, new):
            changed.append(f)
        else:
            skipped.append(f)
    return changed, skipped


def _resolve_files(
    patterns: Iterable[str], ignore: Iterable[str], base_dir: Path
) -> list[Path]:
    """Expand glob patterns while applying ignore rules relative to ``base_dir``.

    This ensures we consistently discover the same set of files regardless of
    the calling context.

    Args:
        patterns: Glob patterns to search for version files.
        ignore: Glob patterns to exclude from results.
        base_dir: Directory relative to which patterns are evaluated.

    Returns:
        List of discovered file paths matching ``patterns`` minus ``ignore``.

    Raises:
        None

    Notes:
        Results are cached based on ``patterns``, ``ignore``, and ``base_dir``. Only
        the most recent resolution is retained for performance.
    """

    base = Path(base_dir).resolve()
    return list(_resolve_files_cached(tuple(patterns), tuple(ignore), str(base)))


# Cache only the most recent file resolution to avoid stale filesystem scans.
@lru_cache(maxsize=1)
def _resolve_files_cached(
    patterns: tuple[str, ...], ignore: tuple[str, ...], base_dir: str
) -> tuple[Path, ...]:
    """Resolve files for caching.

    The resolution is isolated here so we can memoise results without carrying
    the heavier logic of :func:`_resolve_files`.

    Args:
        patterns: Glob patterns to search for version files.
        ignore: Glob patterns to exclude from results.
        base_dir: Directory relative to which patterns are evaluated.

    Returns:
        Tuple of unique file paths matching ``patterns`` minus ``ignore``.

    Raises:
        None
    """

    out: set[Path] = set()
    ignore_list = list(ignore)
    base = Path(base_dir)
    for pat in patterns:
        pat_path = Path(pat)
        search = pat if pat_path.is_absolute() else str(base / pat)
        for match in glob(search, recursive=True):
            p = Path(match)
            if not p.is_file():
                continue
            path_str = str(p)
            try:
                rel_str = str(p.resolve().relative_to(base))
            except ValueError:
                rel_str = path_str
            if any(fnmatch(path_str, ig) or fnmatch(rel_str, ig) for ig in ignore_list):
                continue
            out.add(p)
    # Ensure deterministic ordering for predictable downstream operations.
    return tuple(sorted(out))


def _replace_version(path: Path, old: str, new: str) -> bool:
    """Replace ``old`` version occurrences with ``new`` in ``path``.

    The search uses several patterns to catch common naming conventions without
    false positives.

    Args:
        path: File whose contents should be updated.
        old: Previous version string.
        new: New version string.

    Returns:
        ``True`` if the file was modified, ``False`` otherwise.

    Raises:
        OSError: If the file cannot be read or written.
    """

    text = path.read_text(encoding="utf-8")
    replaced = 0

    def _sub(match: re.Match[str]) -> str:
        nonlocal replaced
        if match.group(2) != old:
            return match.group(0)
        replaced += 1
        return f"{match.group(1)}{new}{match.group(3)}"

    for pattern in _VERSION_RE_PATTERNS:
        text = pattern.sub(_sub, text)
    if replaced:
        path.write_text(text, encoding="utf-8")
        return True
    return False
