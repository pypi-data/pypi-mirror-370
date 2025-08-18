from pathlib import Path

import pytest

from bumpwright.public_api import extract_public_api_from_source, module_name_from_path


def test_extracts_functions_and_methods() -> None:
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
    assert foo.returns == "-> int" or foo.returns.endswith("int")
    assert any(p.name == "y" and p.default is not None for p in foo.params)


def test_respects_class_exports() -> None:
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


def test_module_name_from_path_nested(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    path = root / "a" / "b" / "mod.py"
    assert module_name_from_path(str(root), str(path)) == "a.b.mod"


def test_module_name_from_path_outside_root(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    path = tmp_path / "other" / "mod.py"
    with pytest.raises(ValueError):
        module_name_from_path(str(root), str(path))


def test_param_kinds() -> None:
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


def test_extract_without_exports_includes_public() -> None:
    code = """
def foo():
    pass
def _bar():
    pass
"""
    api = extract_public_api_from_source("pkg.mod", code)
    keys = set(api.keys())
    assert "pkg.mod:foo" in keys
    assert "pkg.mod:_bar" not in keys


def test_empty_exports_exclude_symbols() -> None:
    code = """
__all__ = []
def foo():
    pass
"""
    api = extract_public_api_from_source("pkg.mod", code)
    assert not api


def test_skips_overload_stubs() -> None:
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
