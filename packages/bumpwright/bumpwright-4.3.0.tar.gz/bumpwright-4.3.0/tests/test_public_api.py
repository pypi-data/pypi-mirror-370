from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "bumpwright.public_api",
    Path(__file__).resolve().parents[1] / "bumpwright" / "public_api.py",
)
public_api = importlib.util.module_from_spec(spec)
sys.modules["bumpwright.public_api"] = public_api
assert spec.loader  # noqa: PT018 - ensure loader exists for mypy
spec.loader.exec_module(public_api)
extract_public_api_from_source = public_api.extract_public_api_from_source
module_name_from_path = public_api.module_name_from_path


def test_extracts_functions_and_methods():
    code = """
__all__ = ["foo", "Bar"]
def foo(x: int, y: int = 1) -> int: return x + y
def _hidden(): pass
class Bar:
    def baz(self, q, *, opt=None) -> str: return "ok"
    def _private(self): pass
"""
    api = extract_public_api_from_source("pkg.mod", code)
    keys = set(api.keys())
    assert "pkg.mod:foo" in keys
    assert "pkg.mod:Bar.baz" in keys
    assert "pkg.mod:_hidden" not in keys
    assert "pkg.mod:Bar._private" not in keys

    foo = api["pkg.mod:foo"]
    assert foo.returns == "-> int" or foo.returns.endswith("int")  # libcst emits "-> int" style string
    assert any(p.name == "y" and p.default is not None for p in foo.params)


def test_respects_class_exports():
    code = """
__all__ = ["Visible"]
class Visible:
    def ping(self):
        pass
class Hidden:
    def ping(self):
        pass
"""
    api = extract_public_api_from_source("pkg.mod", code)
    keys = set(api.keys())
    assert "pkg.mod:Visible.ping" in keys
    assert "pkg.mod:Hidden.ping" not in keys


def test_module_name_from_path_nested(tmp_path):
    root = tmp_path / "pkg"
    path = root / "a" / "b" / "mod.py"
    assert module_name_from_path(str(root), str(path)) == "a.b.mod"


def test_module_name_from_path_outside_root(tmp_path):
    root = tmp_path / "pkg"
    path = tmp_path / "other" / "mod.py"
    with pytest.raises(ValueError):
        module_name_from_path(str(root), str(path))


def test_param_kinds():
    code = """
def sample(a, /, b, c=1, *d, e, f=2, **g):
    pass
"""
    api = extract_public_api_from_source("pkg.mod", code)
    params = api["pkg.mod:sample"].params
    assert [(p.name, p.kind, p.default) for p in params] == [
        ("a", "posonly", None),
        ("b", "pos", None),
        ("c", "pos", "1"),
        ("d", "vararg", None),
        ("e", "kwonly", None),
        ("f", "kwonly", "2"),
        ("g", "varkw", None),
    ]


def test_extract_without_exports_includes_public() -> None:
    """Include public symbols when ``__all__`` is absent."""

    code = """
def foo():
    pass
def _bar():
    pass
"""
    api = extract_public_api_from_source("pkg.mod", code)
    assert "pkg.mod:foo" in api
    assert "pkg.mod:_bar" not in api


def test_all_allows_underscore_and_skips_non_strings() -> None:
    """Respect ``__all__`` string entries even if private."""

    code = """
names = ["bar"]
__all__ = ["_hidden"] + names + [1]
def _hidden():
    pass
def bar():
    pass
"""
    api = extract_public_api_from_source("pkg.mod", code)
    keys = set(api.keys())
    assert "pkg.mod:_hidden" in keys
    assert "pkg.mod:bar" in keys


def test_without_all_filters_private_members() -> None:
    """Exclude private classes and methods when ``__all__`` is absent."""

    code = """
class _Hidden:
    def visible(self):
        pass
class Visible:
    def _secret(self):
        pass
    def show(self):
        pass
"""
    api = extract_public_api_from_source("pkg.mod", code)
    keys = set(api.keys())
    assert "pkg.mod:_Hidden.visible" not in keys
    assert "pkg.mod:Visible._secret" not in keys
    assert "pkg.mod:Visible.show" in keys


def test_extract_invalid_code_raises() -> None:
    """Raise ``SyntaxError`` when source cannot be parsed."""

    with pytest.raises(SyntaxError):
        extract_public_api_from_source("pkg.mod", "def bad(:\n pass")


@pytest.mark.parametrize(
    "prefix",
    [
        "__all__ = ['foo'] + ['bar']",
        "names = ['foo']\nextra = ['bar']\n__all__ = names + extra",
    ],
)
def test_extracts_all_from_concatenation(prefix: str) -> None:
    """Detect ``__all__`` constructed via simple concatenation."""

    code = f"""
{prefix}
def foo():
    pass
def bar():
    pass
"""
    api = extract_public_api_from_source("pkg.mod", code)
    keys = set(api.keys())
    assert {"pkg.mod:foo", "pkg.mod:bar"} == keys


def test_custom_private_prefix() -> None:
    code = """
def internal_func():
    pass
def public():
    pass
"""
    api = extract_public_api_from_source("pkg.mod", code, ["internal_"])
    assert "pkg.mod:public" in api
    assert "pkg.mod:internal_func" not in api


def test_skips_overload_stubs() -> None:
    """Ignore overload stubs but keep implementation."""

    code = """
from typing import overload
import typing

@overload
def foo(x: int) -> int: ...
@typing.overload
def foo(x: str) -> str: ...
def foo(x):
    return x
"""
    api = extract_public_api_from_source("pkg.mod", code)
    assert "pkg.mod:foo" in api
    assert len(api) == 1
