from __future__ import annotations

from pathlib import Path

import pytest

from bumpwright.config import Config, Rules, load_config


def test_load_config_parses_analysers(tmp_path: Path) -> None:
    """Enable and disable analysers based on config values."""

    cfg_file = tmp_path / "bumpwright.toml"
    cfg_file.write_text("[analysers]\nweb_routes = true\nmigrations = false\n")
    cfg = load_config(cfg_file)
    assert cfg.analysers.enabled == {"web_routes"}


def test_load_config_defaults_analysers(tmp_path: Path) -> None:
    cfg = load_config(tmp_path / "missing.toml")
    assert cfg.analysers.enabled == set()


def test_load_config_private_prefixes(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bumpwright.toml"
    cfg_file.write_text("[project]\nprivate_prefixes=['__', 'internal_']\n")
    cfg = load_config(cfg_file)
    assert cfg.project.private_prefixes == ["__", "internal_"]


def test_load_config_private_prefixes_default(tmp_path: Path) -> None:
    cfg = load_config(tmp_path / "missing.toml")
    assert cfg.project.private_prefixes == ["_"]


def test_load_config_changelog(tmp_path: Path) -> None:
    cfg_file = tmp_path / "bumpwright.toml"
    cfg_file.write_text(
        "[changelog]\npath='NEWS.md'\ntemplate='tmpl.j2'\nexclude=['^chore']\nrepo_url='https://example.com/repo'\n"
    )
    cfg = load_config(cfg_file)
    assert cfg.changelog.path == "NEWS.md"
    assert cfg.changelog.template == "tmpl.j2"
    assert cfg.changelog.exclude == ["^chore"]
    assert cfg.changelog.repo_url == "https://example.com/repo"


def test_load_config_changelog_default(tmp_path: Path) -> None:
    cfg = load_config(tmp_path / "missing.toml")
    assert cfg.changelog.path == ""
    assert cfg.changelog.template == ""
    assert cfg.changelog.exclude == []
    assert cfg.changelog.repo_url == ""


def test_load_config_repo_url_from_string(monkeypatch) -> None:
    """Parse ``repo_url`` when provided with a TOML string."""

    config_text = "[changelog]\nrepo_url='https://example.com/repo'\n"
    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "read_text", lambda self, encoding="utf-8": config_text)
    cfg = load_config(config_text)
    assert cfg.changelog.repo_url == "https://example.com/repo"


def test_load_config_default_scheme(tmp_path: Path) -> None:
    """Default configuration uses the semantic versioning scheme."""

    cfg = load_config(tmp_path / "missing.toml")
    assert cfg.version.scheme == "semver"


def test_mutating_config_does_not_alter_defaults(tmp_path: Path) -> None:
    """Ensure modifying a loaded config leaves defaults unchanged."""

    defaults = Config()
    cfg = load_config(tmp_path / "missing.toml")
    cfg.project.public_roots.append("src")

    fresh = load_config(tmp_path / "missing.toml")
    assert defaults.project.public_roots == ["."]
    assert fresh.project.public_roots == ["."]


def test_version_ignore_defaults_extend(tmp_path: Path) -> None:
    """Custom version ignores extend the built-in defaults."""

    cfg_file = tmp_path / "bumpwright.toml"
    cfg_file.write_text("[version]\nignore=['custom/**']\n")
    cfg = load_config(cfg_file)
    assert "custom/**" in cfg.version.ignore
    defaults = {
        "build/**",
        "dist/**",
        "*.egg-info/**",
        ".eggs/**",
        ".venv/**",
        "venv/**",
        ".env/**",
        "**/__pycache__/**",
    }
    assert defaults.issubset(set(cfg.version.ignore))


def test_unknown_top_level_section(tmp_path: Path) -> None:
    """Raise an error for unrecognised top-level sections."""

    cfg_file = tmp_path / "bumpwright.toml"
    cfg_file.write_text("[nonsense]\nfoo=1\n")
    with pytest.raises(ValueError) as exc:
        load_config(cfg_file)
    assert "nonsense" in str(exc.value)


def test_unknown_key_in_section(tmp_path: Path) -> None:
    """Raise an error for unrecognised keys within a known section."""

    cfg_file = tmp_path / "bumpwright.toml"
    cfg_file.write_text("[project]\nunknown='x'\n")
    with pytest.raises(ValueError) as exc:
        load_config(cfg_file)
    message = str(exc.value)
    assert "project" in message and "unknown" in message


def test_rules_invalid_return_type_change() -> None:
    """Reject unsupported return type change levels."""

    with pytest.raises(ValueError):
        Rules(return_type_change="patch")


def test_rules_invalid_param_annotation_change() -> None:
    """Reject unsupported parameter annotation change levels."""

    with pytest.raises(ValueError):
        Rules(param_annotation_change="build")


def test_rules_invalid_implementation_change() -> None:
    """Reject unsupported implementation change levels."""

    with pytest.raises(ValueError):
        Rules(implementation_change="build")


def test_load_config_invalid_return_type_change(tmp_path: Path) -> None:
    """Raise an error when config specifies an invalid return type change."""

    cfg_file = tmp_path / "bumpwright.toml"
    cfg_file.write_text("[rules]\nreturn_type_change='patch'\n")
    with pytest.raises(ValueError):
        load_config(cfg_file)


def test_load_config_invalid_param_annotation_change(tmp_path: Path) -> None:
    """Raise an error when config specifies an invalid param annotation change."""

    cfg_file = tmp_path / "bumpwright.toml"
    cfg_file.write_text("[rules]\nparam_annotation_change='build'\n")
    with pytest.raises(ValueError):
        load_config(cfg_file)


def test_load_config_invalid_implementation_change(tmp_path: Path) -> None:
    """Raise an error when config specifies an invalid implementation change."""

    cfg_file = tmp_path / "bumpwright.toml"
    cfg_file.write_text("[rules]\nimplementation_change='build'\n")
    with pytest.raises(ValueError):
        load_config(cfg_file)
