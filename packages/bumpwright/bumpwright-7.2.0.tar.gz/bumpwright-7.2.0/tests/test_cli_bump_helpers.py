import argparse
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest
from cli_helpers import run, setup_repo

from bumpwright.compare import Decision
from bumpwright.config import load_config
from bumpwright.versioning import VersionChange

from bumpwright.cli.bump import (  # isort:skip
    _commit_tag,
    _display_result,
    _safe_changed_paths,
    _prepare_version_files,
    _resolve_pyproject,
    _write_changelog,
    GitDiffError,
)
from bumpwright.cli.changelog import (  # isort:skip
    _build_changelog,
    _read_template,
    get_default_template,
)


def test_prepare_version_files_no_relevant_changes(tmp_path: Path) -> None:
    repo, _, base = setup_repo(tmp_path)
    pyproj = repo / "pyproject.toml"
    pyproj.write_text(pyproj.read_text().replace("0.1.0", "0.1.1"), encoding="utf-8")
    run(["git", "add", "pyproject.toml"], repo)
    run(["git", "commit", "-m", "chore: bump version"], repo)
    cfg = load_config(repo / "bumpwright.toml")
    args = argparse.Namespace(version_path=["pkg*/__init__.py"])
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        paths = _prepare_version_files(cfg, args, pyproj, base, "HEAD")
    finally:
        os.chdir(cwd)
    # Without a ``__version__`` marker, ``__init__.py`` should count as a regular
    # source file, so version files are still returned.
    assert paths == cfg.version.paths


def test_prepare_version_files_wildcard_directory(tmp_path: Path) -> None:
    repo, _, base = setup_repo(tmp_path)
    extra_pkg = repo / "pkg_extra"
    extra_pkg.mkdir()
    mod_file = extra_pkg / "extra.py"
    mod_file.write_text("value = 1\n", encoding="utf-8")
    run(["git", "add", "pkg_extra/extra.py"], repo)
    run(["git", "commit", "-m", "feat: add extra module"], repo)
    cfg = load_config(repo / "bumpwright.toml")
    args = argparse.Namespace(version_path=["pkg*/__init__.py"])
    pyproj = repo / "pyproject.toml"
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        paths = _prepare_version_files(cfg, args, pyproj, base, "HEAD")
    finally:
        os.chdir(cwd)
    assert paths is not None
    assert "pkg*/__init__.py" in paths


def test_prepare_version_files_glob_relative(tmp_path: Path) -> None:
    repo, pkg, base = setup_repo(tmp_path)
    init_file = pkg / "__init__.py"
    init_file.write_text("def foo() -> int:\n    return 2\n", encoding="utf-8")
    run(["git", "add", "pkg/__init__.py"], repo)
    run(["git", "commit", "-m", "chore: modify init"], repo)
    cfg = load_config(repo / "bumpwright.toml")
    args = argparse.Namespace(version_path=None)
    pyproj = repo / "pyproject.toml"
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        paths = _prepare_version_files(cfg, args, pyproj, base, "HEAD")
    finally:
        os.chdir(cwd)
    # Without a ``__version__`` marker, ``__init__.py`` should count as a regular
    # source file, so version files are still returned.
    assert paths == cfg.version.paths


def test_prepare_version_files_glob_absolute(tmp_path: Path) -> None:
    repo, _, base = setup_repo(tmp_path)
    extra_pkg = repo / "pkg_extra"
    extra_pkg.mkdir()
    init_file = extra_pkg / "__init__.py"
    init_file.write_text("value = 1\n", encoding="utf-8")
    run(["git", "add", "pkg_extra/__init__.py"], repo)
    run(["git", "commit", "-m", "chore: add extra init"], repo)
    cfg = load_config(repo / "bumpwright.toml")
    cfg.version.paths = [f"{repo}/pkg*/__init__.py"]
    args = argparse.Namespace(version_path=None)
    pyproj = repo / "pyproject.toml"
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        paths = _prepare_version_files(cfg, args, pyproj, base, "HEAD")
    finally:
        os.chdir(cwd)
    # Even with absolute globs, files lacking ``__version__`` should not be
    # treated as version files, so a bump is still required.
    assert paths == cfg.version.paths


def test_safe_changed_paths_errors(monkeypatch) -> None:
    """Ensure a descriptive error is raised for diff failures."""

    def fail(base: str, head: str) -> set[str]:
        raise subprocess.CalledProcessError(1, ["git", "diff"])

    monkeypatch.setattr("bumpwright.cli.bump.changed_paths", fail)
    with pytest.raises(GitDiffError, match="BASE.*HEAD"):
        _safe_changed_paths("BASE", "HEAD")


def test_resolve_pyproject_missing() -> None:
    """Ensure resolving a missing pyproject raises an informative error."""

    with pytest.raises(
        FileNotFoundError, match="pyproject.toml not found at missing.pyproject"
    ):
        _resolve_pyproject("missing.pyproject")


def test_display_result_json(caplog) -> None:
    args = argparse.Namespace(format="json")
    vc = VersionChange("0.1.0", "0.2.0", "minor", [Path("pyproject.toml")])
    dec = Decision("minor", 1.0, [])
    with caplog.at_level(logging.INFO):
        _display_result(args, vc, dec)
    data = json.loads(caplog.records[0].message)
    assert data["new_version"] == "0.2.0"
    assert data["skipped"] == []


def test_display_result_text_skipped(caplog) -> None:
    args = argparse.Namespace(format="text")
    vc = VersionChange(
        "0.1.0",
        "0.2.0",
        "minor",
        [Path("pyproject.toml")],
        [Path("extra.py")],
    )
    dec = Decision("minor", 1.0, [])
    with caplog.at_level(logging.INFO):
        _display_result(args, vc, dec)
    out = "\n".join(record.message for record in caplog.records)
    assert "Skipped files: extra.py" in out


def test_write_changelog_to_file(tmp_path: Path) -> None:
    args = argparse.Namespace(changelog=str(tmp_path / "CHANGELOG.md"))
    content = "entry\n"
    _write_changelog(args, content)
    assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8") == content


def test_read_template_custom(tmp_path: Path) -> None:
    tpl = tmp_path / "tpl.j2"
    tpl.write_text("Hello", encoding="utf-8")
    assert _read_template(str(tpl)) == "Hello"


def test_read_template_default(monkeypatch) -> None:
    def fake_default() -> str:
        return "Hi"

    monkeypatch.setattr("bumpwright.cli.changelog.get_default_template", fake_default)
    assert _read_template(None) == "Hi"


def test_get_default_template_reads_file() -> None:
    expected = (
        Path(__file__).resolve().parents[1]
        / "bumpwright"
        / "templates"
        / "changelog.md.j2"
    ).read_text(encoding="utf-8")
    assert get_default_template() == expected


def test_build_changelog_uses_read_template(monkeypatch) -> None:
    args = argparse.Namespace(
        changelog="CHANGELOG.md", head="HEAD", repo_url=None, changelog_template=None
    )
    monkeypatch.setattr(
        "bumpwright.cli.changelog.collect_commits", lambda base, head: []
    )
    monkeypatch.setattr("bumpwright.cli.changelog.last_release_commit", lambda: None)
    called = False

    def fake_read(path: str | None) -> str:
        nonlocal called
        called = True
        assert path is None
        return "Version={{ version }}"

    monkeypatch.setattr("bumpwright.cli.changelog._read_template", fake_read)
    result = _build_changelog(args, "0.2.0")
    assert called is True
    assert result == "Version=0.2.0\n"


def test_build_changelog_excludes_patterns(monkeypatch) -> None:
    args = argparse.Namespace(
        changelog="CHANGELOG.md",
        head="HEAD",
        repo_url=None,
        changelog_template=None,
        changelog_exclude=["^chore"],
    )
    commits = [("1", "feat: add", ""), ("2", "chore: skip", "")]
    monkeypatch.setattr(
        "bumpwright.cli.changelog.collect_commits", lambda base, head: commits
    )
    monkeypatch.setattr("bumpwright.cli.changelog.last_release_commit", lambda: None)
    result = _build_changelog(args, "0.2.0")
    assert "feat: add" in result
    assert "chore: skip" not in result


def test_build_changelog_includes_repo_links(monkeypatch) -> None:
    """Commit entries include repository links when ``repo_url`` is set."""

    args = argparse.Namespace(
        changelog="CHANGELOG.md",
        head="HEAD",
        repo_url="https://example.com/repo",
        changelog_template=None,
        changelog_exclude=[],
    )
    commits = [("abc1234", "feat: test", "")]
    monkeypatch.setattr(
        "bumpwright.cli.changelog.collect_commits", lambda base, head: commits
    )
    monkeypatch.setattr("bumpwright.cli.changelog.last_release_commit", lambda: None)
    monkeypatch.setattr("bumpwright.cli.changelog.tag_for_commit", lambda ref: None)
    monkeypatch.setattr(
        "bumpwright.cli.changelog.collect_contributors", lambda base, head: []
    )
    # Timestamps use ``datetime.now`` and are not asserted here.
    result = _build_changelog(args, "1.0.0")
    assert "[abc1234](https://example.com/repo/commit/abc1234)" in result


def test_build_changelog_single_git_invocation(monkeypatch) -> None:
    """Changelog generation should batch commit lookups into one git call."""

    args = argparse.Namespace(
        changelog="CHANGELOG.md",
        head="HEAD",
        repo_url=None,
        changelog_template=None,
        changelog_exclude=[],
    )
    monkeypatch.setattr("bumpwright.cli.changelog.last_release_commit", lambda: None)
    monkeypatch.setattr("bumpwright.cli.changelog.tag_for_commit", lambda ref: None)
    monkeypatch.setattr(
        "bumpwright.cli.changelog.collect_contributors", lambda base, head: []
    )
    monkeypatch.setattr(
        "bumpwright.cli.changelog._read_template", lambda path: "{{ commits|length }}"
    )
    calls: list[list[str]] = []

    def spy(cmd: list[str], cwd: str | None = None) -> str:
        calls.append(cmd)
        return "abc123\x00feat: add\x00\x00"

    monkeypatch.setattr("bumpwright.gitutils._run", spy)
    result = _build_changelog(args, "1.0.0")
    assert result == "1\n"
    assert len(calls) == 1


def test_build_changelog_utc_timestamp(monkeypatch) -> None:
    """Timestamps in the changelog are rendered in UTC."""

    args = argparse.Namespace(
        changelog="CHANGELOG.md",
        head="HEAD",
        repo_url=None,
        changelog_template=None,
        changelog_exclude=[],
    )
    monkeypatch.setattr("bumpwright.cli.changelog.last_release_commit", lambda: None)
    monkeypatch.setattr(
        "bumpwright.cli.changelog.collect_commits",
        lambda base, head: [("abc123", "feat: add", "")],
    )
    monkeypatch.setattr("bumpwright.cli.changelog.tag_for_commit", lambda ref: None)
    monkeypatch.setattr(
        "bumpwright.cli.changelog.collect_contributors", lambda base, head: []
    )
    monkeypatch.setattr(
        "bumpwright.cli.changelog._read_template",
        lambda path: "D={{ date }} T={{ release_datetime_iso }}",
    )

    fixed = datetime(2024, 5, 1, 10, 30, tzinfo=timezone.utc)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz: timezone | None = None) -> datetime:
            assert tz is timezone.utc
            return fixed

    monkeypatch.setattr("bumpwright.cli.changelog.datetime", FixedDateTime)
    result = _build_changelog(args, "1.0.0")
    assert result == "D=2024-05-01 T=2024-05-01T10:30:00+00:00\n"


def test_build_changelog_breaking_footer(monkeypatch) -> None:
    """Detect breaking changes declared in commit footers."""

    args = argparse.Namespace(
        changelog="CHANGELOG.md",
        head="HEAD",
        repo_url=None,
        changelog_template=None,
        changelog_exclude=[],
    )
    commits = [
        ("abc123", "feat: add", "Body\n\nBREAKING CHANGE: API"),
    ]
    monkeypatch.setattr(
        "bumpwright.cli.changelog.collect_commits", lambda base, head: commits
    )
    monkeypatch.setattr("bumpwright.cli.changelog.last_release_commit", lambda: None)
    monkeypatch.setattr("bumpwright.cli.changelog.tag_for_commit", lambda ref: None)
    monkeypatch.setattr(
        "bumpwright.cli.changelog.collect_contributors", lambda base, head: []
    )
    monkeypatch.setattr(
        "bumpwright.cli.changelog._read_template",
        lambda path: "{{ breaking_changes[0] }}",
    )
    result = _build_changelog(args, "1.0.0")
    assert result == "API\n"


def test_build_changelog_single_commit(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Gracefully handle repositories with only a single commit."""

    repo, _, _ = setup_repo(tmp_path)
    args = argparse.Namespace(
        changelog="CHANGELOG.md",
        head="HEAD",
        repo_url=None,
        changelog_template=None,
        changelog_exclude=[],
    )
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        with caplog.at_level(logging.WARNING, logger="bumpwright.cli.changelog"):
            result = _build_changelog(args, "0.2.0")
    finally:
        os.chdir(cwd)
    assert result is None
    assert "Failed to collect commits" in caplog.text


def test_commit_tag_existing_tag(tmp_path: Path) -> None:
    repo, _, _ = setup_repo(tmp_path)
    pyproj = repo / "pyproject.toml"
    # Simulate bumping to a new version that already has a tag
    pyproj.write_text(pyproj.read_text().replace("0.1.0", "0.1.1"), encoding="utf-8")
    run(["git", "tag", "v0.1.1"], repo)
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        with pytest.raises(RuntimeError, match="Tag v0.1.1 already exists"):
            _commit_tag(["pyproject.toml"], "0.1.1", commit=True, tag=True)
    finally:
        os.chdir(cwd)
    head = run(["git", "log", "-1", "--pretty=%s"], repo)
    assert head == "base"


def test_commit_tag_stages_all_files(tmp_path: Path) -> None:
    repo, pkg, _ = setup_repo(tmp_path)
    pyproj = repo / "pyproject.toml"
    init_file = pkg / "__init__.py"
    pyproj.write_text(pyproj.read_text().replace("0.1.0", "0.1.1"), encoding="utf-8")
    init_file.write_text(init_file.read_text() + "\n# change", encoding="utf-8")
    cwd = os.getcwd()
    os.chdir(repo)
    try:
        _commit_tag([pyproj, init_file], "0.1.1", commit=True, tag=False)
    finally:
        os.chdir(cwd)
    files = run(
        ["git", "show", "--pretty=format:", "--name-only", "HEAD"], repo
    ).splitlines()
    assert "pyproject.toml" in files
    assert "pkg/__init__.py" in files
    msg = run(["git", "log", "-1", "--pretty=%s"], repo)
    assert msg == "chore(release): 0.1.1"


def test_commit_tag_no_action() -> None:
    """Skip processing when neither commit nor tag is requested."""

    _commit_tag([], "1.0.0", False, False)


def test_commit_tag_creates_tag(monkeypatch: pytest.MonkeyPatch) -> None:
    """Create a tag when requested and it does not exist."""

    calls: list[list[str]] = []

    def fake_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
        calls.append(cmd)
        if cmd[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(cmd, 1)
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    _commit_tag([], "1.0.0", commit=False, tag=True)
    assert any(cmd[:2] == ["git", "tag"] for cmd in calls)


def test_resolve_pyproject_uses_find(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Fallback to ``find_pyproject`` when path is a directory."""

    target = tmp_path / "pyproject.toml"
    target.write_text("", encoding="utf-8")
    monkeypatch.setattr("bumpwright.cli.bump.find_pyproject", lambda: target)
    assert _resolve_pyproject("foo/pyproject.toml") == target


def test_display_result_md(caplog: pytest.LogCaptureFixture) -> None:
    """Markdown format lists updated and skipped files."""

    args = argparse.Namespace(format="md")
    vc = VersionChange("0.1.0", "0.2.0", "minor", [Path("a")], [Path("b")])
    dec = Decision("minor", 1.0, [])
    with caplog.at_level(logging.INFO):
        _display_result(args, vc, dec)
    out = "\n".join(r.message for r in caplog.records)
    assert "Updated files" in out and "Skipped files" in out
