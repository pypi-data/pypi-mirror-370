"""Command-line interface for the :mod:`bumpwright` project."""

from __future__ import annotations

import argparse
import logging
import os
import sys

try:
    import argcomplete  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional dependency
    argcomplete = None

from ..analysers import available
from ..gitutils import fetch_tags


def _env_flag(name: str) -> bool:
    """Return truthy value of an environment variable.

    Args:
        name: Environment variable to query.

    Returns:
        ``True`` if the variable is set to a truthy value, otherwise ``False``.
    """

    return os.getenv(name, "").lower() in {"1", "true", "yes", "on"}


def _env_list(name: str) -> list[str] | None:
    """Return environment variable split on commas.

    Args:
        name: Environment variable to query.

    Returns:
        List of stripped values if the variable is set, otherwise ``None``.
    """

    value = os.getenv(name)
    if value:
        return [part.strip() for part in value.split(",") if part.strip()]
    return None


def add_ref_options(parser: argparse.ArgumentParser) -> None:
    """Attach git reference options to ``parser``.

    Args:
        parser: Subparser to which the ``--base`` and ``--head`` options are added.
    """

    parser.add_argument(
        "--base",
        default=os.getenv("BUMPWRIGHT_BASE"),
        help=(
            "Base git reference when auto-deciding the level. Defaults to the last release "
            "commit or the previous commit (HEAD^)."
        ),
    )
    parser.add_argument(
        "--head",
        default=os.getenv("BUMPWRIGHT_HEAD", "HEAD"),
        help="Head git reference; defaults to the current HEAD.",
    )


def add_analyser_toggles(parser: argparse.ArgumentParser) -> None:
    """Attach analyser enable/disable flags to ``parser``.

    Args:
        parser: Subparser receiving analyser toggling options.
    """

    parser.add_argument(
        "--enable-analyser",
        action="append",
        dest="enable_analyser",
        default=_env_list("BUMPWRIGHT_ENABLE_ANALYSER"),
        help="Enable analyser NAME (repeatable) in addition to configuration.",
    )
    parser.add_argument(
        "--disable-analyser",
        action="append",
        dest="disable_analyser",
        default=_env_list("BUMPWRIGHT_DISABLE_ANALYSER"),
        help="Disable analyser NAME (repeatable) even if configured.",
    )


from .bump import bump_command  # noqa: E402
from .decide import add_decide_arguments, decide_command  # noqa: E402
from .history import history_command  # noqa: E402
from .init import init_command  # noqa: E402


def _build_init_subparser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> argparse.ArgumentParser:
    """Create the ``init`` subparser.

    Args:
        subparsers: Container returned by :meth:`argparse.ArgumentParser.add_subparsers`.

    Returns:
        The newly created ``init`` subparser.
    """

    parser = subparsers.add_parser(
        "init",
        help="Create baseline release commit",
        description=(
            "Create an empty 'chore(release): initialise baseline' commit to establish a comparison point for future bumps."
        ),
    )
    parser.add_argument(
        "--summary",
        choices=["table", "json"],
        nargs="?",
        const="table",
        default=os.getenv("BUMPWRIGHT_SUMMARY"),
        help="Show project summary after initialisation in the chosen format.",
    )
    parser.set_defaults(func=init_command)
    return parser


def _build_decide_subparser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> argparse.ArgumentParser:
    """Create the ``decide`` subparser."""

    parser = subparsers.add_parser(
        "decide",
        help="Suggest a version bump",
        description="Compare two git references and report the required semantic version level.",
    )
    add_decide_arguments(parser)
    parser.set_defaults(func=decide_command)
    return parser


def _build_bump_subparser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> argparse.ArgumentParser:
    """Create the ``bump`` subparser.

    Args:
        subparsers: Container returned by :meth:`argparse.ArgumentParser.add_subparsers`.

    Returns:
        The newly created ``bump`` subparser.
    """

    parser = subparsers.add_parser(
        "bump",
        help="Apply a version bump",
        description="Update project version metadata and optionally commit and tag the change.",
    )
    add_ref_options(parser)
    parser.add_argument(
        "--format",
        choices=["text", "md", "json"],
        default=os.getenv("BUMPWRIGHT_FORMAT", "text"),
        help="Output style: plain text, Markdown, or machine-readable JSON.",
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
    add_analyser_toggles(parser)
    parser.add_argument(
        "--pyproject",
        default=os.getenv("BUMPWRIGHT_PYPROJECT", "pyproject.toml"),
        help="Path to the project's pyproject.toml file.",
    )
    parser.add_argument(
        "--version-path",
        action="append",
        dest="version_path",
        default=_env_list("BUMPWRIGHT_VERSION_PATH"),
        help=(
            "Additional glob pattern for files containing the project version "
            "(repeatable). Defaults include pyproject.toml, setup.py, setup.cfg, "
            "and any __init__.py, version.py, or _version.py files."
        ),
    )
    parser.add_argument(
        "--version-ignore",
        action="append",
        dest="version_ignore",
        default=_env_list("BUMPWRIGHT_VERSION_IGNORE"),
        help=("Glob pattern for paths to exclude from version updates (repeatable)."),
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_COMMIT"),
        help="Create a git commit for the version change.",
    )
    parser.add_argument(
        "--tag",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_TAG"),
        help="Create a git tag for the new version.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_DRY_RUN"),
        help="Display the new version without modifying any files.",
    )
    parser.add_argument(
        "--changelog",
        nargs="?",
        const="-",
        default=os.getenv("BUMPWRIGHT_CHANGELOG"),
        help=(
            "Append release notes to FILE or stdout when no path is given. "
            "Defaults to [changelog].path in configuration when omitted."
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
    parser.set_defaults(func=bump_command)
    return parser


def _build_history_subparser(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> argparse.ArgumentParser:
    """Create the ``history`` subparser.

    Args:
        subparsers: Container returned by :meth:`argparse.ArgumentParser.add_subparsers`.

    Returns:
        The newly created ``history`` subparser.
    """

    parser = subparsers.add_parser(
        "history",
        help="List existing git tags",
        description="List git tags with their version numbers.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "md", "json"],
        default=os.getenv("BUMPWRIGHT_FORMAT", "text"),
        help="Output style: plain text, Markdown, or machine-readable JSON.",
    )
    parser.add_argument(
        "--local-time",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_LOCAL_TIME"),
        help="Display commit dates in local time instead of ISO-8601.",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_STATS"),
        help="Include line change statistics between successive tags.",
    )
    parser.add_argument(
        "--rollback",
        metavar="TAG",
        default=os.getenv("BUMPWRIGHT_ROLLBACK"),
        help="Delete TAG and restore files to the previous commit.",
    )
    parser.add_argument(
        "--purge",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_PURGE"),
        help="Remove all bumpwright release tags and commits, restoring versioned files.",
    )
    parser.set_defaults(func=history_command)
    return parser


def get_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the command-line interface.

    Example:
        >>> parser = get_parser()
        >>> parser.prog
        'bumpwright'
    """

    avail = ", ".join(available()) or "none"
    parser = argparse.ArgumentParser(
        prog="bumpwright",
        description=(
            f"Suggest and apply semantic version bumps. Available analysers: {avail}."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        default=os.getenv("BUMPWRIGHT_CONFIG", "bumpwright.toml"),
        help="Path to configuration file.",
    )

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_QUIET"),
        help="Only display warnings and errors.",
    )
    verbosity.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=_env_flag("BUMPWRIGHT_VERBOSE"),
        help="Show debug messages.",
    )

    sub = parser.add_subparsers(dest="cmd")
    _build_init_subparser(sub)
    _build_decide_subparser(sub)
    _build_bump_subparser(sub)
    _build_history_subparser(sub)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``bumpwright`` CLI.

    Args:
        argv: Optional sequence of command-line arguments. Defaults to
            ``None`` to use ``sys.argv``.

    Returns:
        Process exit code; ``0`` indicates success.

    Example:
        >>> main(['--help'])  # doctest: +SKIP
        0
    """

    parser = get_parser()
    if argcomplete is not None:  # pragma: no cover - exercised via shell
        argcomplete.autocomplete(parser)
    args = parser.parse_args(argv)
    root = logging.getLogger()
    if not root.hasHandlers():
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    if getattr(args, "quiet", False):
        root.setLevel(logging.WARNING)
    elif getattr(args, "verbose", False):
        root.setLevel(logging.DEBUG)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    if getattr(args, "cmd", None) in {"history", "bump"}:
        fetch_tags()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
