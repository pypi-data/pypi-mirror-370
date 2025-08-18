"""Version scheme implementations for bumpwright."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from .types import BumpLevel

# SemVer segments disallow leading zeros per specification.
_SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-.]+))?(?:\+([0-9A-Za-z-.]+))?$")

# CalVer ``YYYY.MM.PATCH`` with optional prerelease and build segments.
_CALVER_RE = re.compile(r"^(\d{4})\.(0[1-9]|1[0-2])\.(\d+)(?:-([0-9A-Za-z-.]+))?(?:\+([0-9A-Za-z-.]+))?$")


def _bump_segment(segment: str | None, default: str) -> str:
    """Increment the last numeric component of ``segment``.

    Args:
        segment: Existing dot-separated identifier string.
        default: Prefix used when ``segment`` is ``None``.

    Returns:
        Updated identifier string with the last numeric part incremented. When
        no numeric part is present, ``.1`` is appended.
    """

    if not segment:
        return f"{default}.1"
    parts = segment.split(".")
    for i in range(len(parts) - 1, -1, -1):
        if parts[i].isdigit():
            parts[i] = str(int(parts[i]) + 1)
            return ".".join(parts)
    parts.append("1")
    return ".".join(parts)


class VersionScheme(Protocol):
    """Protocol for version bumping strategies."""

    def bump(self, version: str, level: BumpLevel) -> str:
        """Return ``version`` bumped by ``level``.

        Args:
            version: Version string to bump.
            level: Bump level to apply.

        Returns:
            The bumped version string.
        """


@dataclass
class SemverScheme:
    """Semantic versioning following the ``MAJOR.MINOR.PATCH`` pattern."""

    def bump(self, version: str, level: BumpLevel) -> str:
        """Bump a semantic version string.

        Args:
            version: Version string in ``MAJOR.MINOR.PATCH`` form with optional
                prerelease or build metadata.
            level: Bump level to apply.

        Returns:
            The bumped semantic version string. ``major``, ``minor``, and
            ``patch`` bumps reset any prerelease or build information.

        Raises:
            ValueError: If ``level`` is unknown or ``version`` is invalid.

        Example:
            >>> SemverScheme().bump('1.2.3', 'minor')
            '1.3.0'
        """

        match = _SEMVER_RE.match(version)
        if not match:
            raise ValueError(f"Invalid semantic version: {version}")
        major, minor, patch, pre, build = match.groups()
        parts = [int(major), int(minor), int(patch)]
        if level == "major":
            parts = [parts[0] + 1, 0, 0]
            pre = None
            build = None
        elif level == "minor":
            parts = [parts[0], parts[1] + 1, 0]
            pre = None
            build = None
        elif level == "patch":
            parts = [parts[0], parts[1], parts[2] + 1]
            pre = None
            build = None
        elif level == "pre":
            pre = _bump_segment(pre, "rc")
        elif level == "build":
            build = _bump_segment(build, "build")
        else:  # pragma: no cover - defensive
            raise ValueError(f"Unknown level {level}")

        out = f"{parts[0]}.{parts[1]}.{parts[2]}"
        if pre:
            out += f"-{pre}"
        if build:
            out += f"+{build}"
        return out


@dataclass
class CalverScheme:
    """Calendar versioning using ``YYYY.MM.PATCH`` segments."""

    def bump(self, version: str, level: BumpLevel) -> str:
        """Bump a calendar version string.

        If ``level`` is ``patch`` and the current date differs from the
        ``version`` year or month, the year and month are reset to today and the
        patch number is set to ``0``.

        Args:
            version: Version string in ``YYYY.MM.PATCH`` form with optional
                prerelease or build metadata.
            level: Bump level to apply.

        Returns:
            The bumped calendar version string.

        Raises:
            ValueError: If ``level`` is unknown or ``version`` is invalid.

        Example:
            >>> CalverScheme().bump('2023.01.0', 'patch').split('.')[:2]
            ['2023', '01']
        """

        match = _CALVER_RE.match(version)
        if not match:
            raise ValueError(f"Invalid calendar version: {version}")
        year, month, patch, pre, build = match.groups()
        today = date.today()
        y, m, p = int(year), int(month), int(patch)

        if level in {"major", "minor"}:
            y, m, p = today.year, today.month, 0
            pre = None
            build = None
        elif level == "patch":
            if today.year != y or today.month != m:
                y, m, p = today.year, today.month, 0
            else:
                p += 1
            pre = None
            build = None
        elif level == "pre":
            pre = _bump_segment(pre, "rc")
        elif level == "build":
            build = _bump_segment(build, "build")
        else:  # pragma: no cover - defensive
            raise ValueError(f"Unknown level {level}")

        out = f"{y:04d}.{m:02d}.{p}"
        if pre:
            out += f"-{pre}"
        if build:
            out += f"+{build}"
        return out


_SCHEMES: dict[str, VersionScheme] = {
    "semver": SemverScheme(),
    "calver": CalverScheme(),
}


def get_version_scheme(name: str) -> VersionScheme:
    """Return the version scheme instance for ``name``.

    Args:
        name: Identifier of the desired scheme.

    Returns:
        Concrete :class:`VersionScheme` implementation.

    Raises:
        ValueError: If ``name`` is not recognised.

    Example:
        >>> get_version_scheme('semver').bump('1.0.0', 'patch')
        '1.0.1'
    """

    try:
        return _SCHEMES[name]
    except KeyError as exc:  # pragma: no cover - simple passthrough
        raise ValueError(f"Unknown version scheme: {name}") from exc


__all__ = [
    "VersionScheme",
    "SemverScheme",
    "CalverScheme",
    "get_version_scheme",
]
