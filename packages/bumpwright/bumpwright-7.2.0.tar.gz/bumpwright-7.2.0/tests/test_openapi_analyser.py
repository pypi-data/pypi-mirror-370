from __future__ import annotations

import logging

import pytest

from bumpwright.analysers import openapi
from bumpwright.analysers.openapi import OpenAPIAnalyser, Spec, _parse_spec, diff_specs
from bumpwright.config import Config


def _build(src: str) -> Spec:
    """Parse a spec snippet into a :class:`Spec`."""

    return _parse_spec(src)


def test_removed_endpoint_is_major() -> None:
    """Removing an endpoint triggers a major impact."""

    old = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get: {}
""",
    )
    new = _build(
        """
openapi: 3.0.0
paths: {}
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "major" for i in impacts)


def test_added_endpoint_is_minor() -> None:
    """Adding a new endpoint triggers a minor impact."""

    old = _build(
        """
openapi: 3.0.0
paths: {}
""",
    )
    new = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    post: {}
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "minor" for i in impacts)


def test_schema_change_is_major() -> None:
    """Modifying a schema definition is a major impact."""

    old = _build(
        """
openapi: 3.0.0
components:
  schemas:
    Pet:
      type: object
      properties:
        id:
          type: integer
""",
    )
    new = _build(
        """
openapi: 3.0.0
components:
  schemas:
    Pet:
      type: object
      properties:
        id:
          type: string
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "major" and i.symbol == "Pet" for i in impacts)


def test_parameter_addition_is_minor() -> None:
    """Adding a parameter triggers a minor impact."""

    old = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      parameters:
        - name: id
          in: query
          required: true
""",
    )
    new = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      parameters:
        - name: id
          in: query
          required: true
        - name: type
          in: query
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "minor" and i.reason == "Added parameter type" for i in impacts)


def test_parameter_removal_is_major() -> None:
    """Removing a parameter triggers a major impact."""

    old = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      parameters:
        - name: id
          in: query
          required: true
        - name: type
          in: query
""",
    )
    new = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      parameters:
        - name: id
          in: query
          required: true
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "major" and i.reason == "Removed parameter type" for i in impacts)


def test_parameter_required_toggle_is_major() -> None:
    """Toggling a parameter to required triggers a major impact."""

    old = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      parameters:
        - name: id
          in: query
""",
    )
    new = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      parameters:
        - name: id
          in: query
          required: true
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "major" and i.reason == "Parameter id now required" for i in impacts)


def test_parameter_required_toggle_to_optional_is_minor() -> None:
    """Making a parameter optional triggers a minor impact."""

    old = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      parameters:
        - name: id
          in: query
          required: true
""",
    )
    new = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      parameters:
        - name: id
          in: query
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "minor" and i.reason == "Parameter id no longer required" for i in impacts)


def test_response_schema_change_is_major() -> None:
    """Modifying a response schema triggers a major impact."""

    old = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      responses:
        "200":
          content:
            application/json:
              schema:
                type: string
""",
    )
    new = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      responses:
        "200":
          content:
            application/json:
              schema:
                type: integer
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "major" and i.reason == "Changed response 200 schema (application/json)" for i in impacts)


def test_response_schema_change_multiple_media_types_is_major() -> None:
    """Changing schemas for multiple media types triggers separate impacts."""

    old = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      responses:
        "200":
          content:
            application/json:
              schema:
                type: string
            application/xml:
              schema:
                type: string
""",
    )
    new = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      responses:
        "200":
          content:
            application/json:
              schema:
                type: integer
            application/xml:
              schema:
                type: boolean
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "major" and i.reason == "Changed response 200 schema (application/json)" for i in impacts)
    assert any(i.severity == "major" and i.reason == "Changed response 200 schema (application/xml)" for i in impacts)


def test_invalid_yaml_returns_empty_spec(caplog) -> None:
    """Invalid YAML logs a warning and yields an empty spec."""

    with caplog.at_level(logging.WARNING):
        spec = _parse_spec("openapi: 3.0.0: bad")
    assert spec == Spec(endpoints=set(), schemas={}, operations={})
    assert any("Failed to parse OpenAPI spec" in r.message for r in caplog.records)


def test_schema_addition_is_minor() -> None:
    """Adding a new schema triggers a minor impact."""

    old = _build(
        """
openapi: 3.0.0
components:
  schemas: {}
""",
    )
    new = _build(
        """
openapi: 3.0.0
components:
  schemas:
    Pet:
      type: object
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "minor" and i.reason == "Added schema" and i.symbol == "Pet" for i in impacts)


def test_schema_removal_is_major() -> None:
    """Removing a schema triggers a major impact."""

    old = _build(
        """
openapi: 3.0.0
components:
  schemas:
    Pet:
      type: object
""",
    )
    new = _build(
        """
openapi: 3.0.0
components:
  schemas: {}
""",
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "major" and i.reason == "Removed schema" and i.symbol == "Pet" for i in impacts)


def test_response_addition_and_removal() -> None:
    """Adding or removing responses affects impact severity."""

    old = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                type: string
"""
    )
    new = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get: {}
"""
    )
    impacts = diff_specs(old, new)
    assert any(i.severity == "major" and i.reason == "Removed response 200 (application/json)" for i in impacts)

    old_empty = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get: {}
"""
    )
    new_resp = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                type: string
"""
    )
    impacts = diff_specs(old_empty, new_resp)
    assert any(i.severity == "minor" and i.reason == "Added response 200 (application/json)" for i in impacts)


def test_path_level_parameters_included() -> None:
    """Path-level parameters are merged into operation parameters."""

    spec = _build(
        """
openapi: 3.0.0
paths:
  /pets:
    parameters:
      - name: id
        in: path
        required: true
    get: {}
""",
    )
    op = spec.operations[("/pets", "GET")]
    assert op.parameters[("id", "path")] is True


def test_openapi_analyser_collect_and_compare(monkeypatch: pytest.MonkeyPatch) -> None:
    """Collect merges specs and compare delegates to ``diff_specs``."""

    cfg = Config()
    cfg.openapi.paths = ["one.yml", "two.yml"]
    analyser = OpenAPIAnalyser(cfg)

    content = """
openapi: 3.0.0
paths:
  /a:
    get: {}
"""
    monkeypatch.setattr(
        openapi,
        "read_files_at_ref",
        lambda ref, paths: {"one.yml": content, "two.yml": None},
    )
    spec = analyser.collect("HEAD")
    assert spec.endpoints == {("/a", "GET")}

    impacts = analyser.compare(spec, Spec(endpoints=set(), schemas={}, operations={}))
    assert any(i.reason == "Removed endpoint" for i in impacts)
