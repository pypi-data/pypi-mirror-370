# bumpwright

![Coverage](https://lewis-morris.github.io/bumpwright/_static/badges/coverage.svg)
![Version](https://lewis-morris.github.io/bumpwright/_static/badges/version.svg)
![Python Versions](https://lewis-morris.github.io/bumpwright/_static/badges/python.svg)
![License](https://lewis-morris.github.io/bumpwright/_static/badges/license.svg)


Bumpwright compares two Git refs, inspects your **public API**, and recommends (or applies) the correct semantic version bump. It can also update version strings in your project and render changelog entries from your commits.

**Docs:** https://lewis-morris.github.io/bumpwright

---

## Why Bumpwright?

- **Code-first accuracy** – infers breaking/minor/patch from exported symbols, not commit messages.  
- **Optional analysers** – enable checks for CLI, web routes, migrations, OpenAPI/GraphQL, and more.
- **CI-friendly** – print a decision (`text|md|json`) or apply + tag releases automatically.

See feature overviews and trade-offs in the [Introduction](https://lewis-morris.github.io/bumpwright/#introduction).

---

## Install

```bash
pip install bumpwright  # Python 3.11+
```

Bumpwright now uses Python's built-in `tomllib`, removing the need for the
external `tomli` dependency.

Full details: [Installation](https://lewis-morris.github.io/bumpwright/get-started.html#installation)

---

## TL;DR (90 seconds)

```bash
# 1) Create a baseline release commit once
bumpwright init

# 2) Ask Bumpwright what the next version should be
bumpwright bump --decide

# 3) Apply it, update files, commit and tag
bumpwright bump --commit --tag
```

What the decision means and examples: [Quickstart](https://lewis-morris.github.io/bumpwright/get-started.html#quickstart) • Command flags: [Usage → bump](https://lewis-morris.github.io/bumpwright/usage/bump.html)

| Command | Purpose |
|---------|---------|
| [`bumpwright init`](https://lewis-morris.github.io/bumpwright/usage/init.html) | Create a baseline release commit. |
| [`bumpwright bump`](https://lewis-morris.github.io/bumpwright/usage/bump.html) | Determine and apply the next version. |

---

## Configuration (minimal)

Bumpwright reads `bumpwright.toml` (you can change with `--config`). Defaults are sensible; start small and opt-in extras as needed.

```toml
# bumpwright.toml
[project]
public_roots = ["."]
private_prefixes = ["_"]  # names starting with "_" are ignored as private

[analysers]
cli = true         # set true to enable
grpc = false
web_routes = false
migrations = false
openapi = false
graphql = false

[changelog]
# path = "CHANGELOG.md"   # optional default target for --changelog
repo_url = "https://github.com/me/project"  # link commits and compares

[version]
scheme = "semver"   # "semver" | "calver"
# paths / ignore have robust defaults
```

All options and defaults: [Configuration](https://lewis-morris.github.io/bumpwright/configuration.html) • Versioning schemes: [Versioning](https://lewis-morris.github.io/bumpwright/versioning.html)

---

## Output & Changelog

- Choose output with `--format text|md|json` for human/CI consumption.
- Generate release notes with a Jinja2 template via `--changelog` (and `--repo-url` or `[changelog].repo_url` for compare/commit links).

Template context includes: `version`, `date`, `release_datetime_iso`, `commits[sha,subject,link]`, `previous_tag`, `compare_url`, `contributors[name,link]`, `breaking_changes`, `repo_url`.

Learn more & ready-to-copy templates:  
- [Changelog → Template variables](https://lewis-morris.github.io/bumpwright/changelog/template.html)  
- [Changelog → Examples](https://lewis-morris.github.io/bumpwright/changelog/examples.html)

---

## Analysers (opt-in)

Enable what you need in `[analysers]` or per-run with `--enable-analyser/--disable-analyser`.

- **Python API (default)** – respects `__all__`; otherwise public = names not starting with `_`.  
- **CLI** – detects changes to argparse/Click commands.  
- **Web routes** – Flask/FastAPI route changes.  
- **Migrations** – Alembic schema impacts.  
- **OpenAPI** – spec diffs.  
- **GraphQL** – schema diffs.

Overview & per-analyser docs: [Analysers](https://lewis-morris.github.io/bumpwright/analysers/)

---

## GitHub Actions (CI)

Common workflows are prebuilt:

- **Auto-bump on push** (commit + tag + append changelog)  
- **PR check** (report decision only)  
- **Manual release** (on dispatch)

Copy/paste from: [CI/CD (GitHub Actions)](https://lewis-morris.github.io/bumpwright/recipes/github-actions.html)

---

## Contributing & Roadmap

Issues and PRs welcome. See [Contributing](https://lewis-morris.github.io/bumpwright/contributing.html) and planned work in the [Roadmap](https://lewis-morris.github.io/bumpwright/roadmap.html).

**License:** [MIT](./LICENSE)
