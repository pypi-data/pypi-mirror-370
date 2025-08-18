import pytest

from bumpwright import public_api


def test_build_api_skips_invalid_modules(monkeypatch: pytest.MonkeyPatch) -> None:
    """`build_api_at_ref` should ignore files that fail to parse."""

    def fake_iter_py_files_at_ref(ref: str, roots, ignore_globs=None):
        yield "pkg/good.py", "def foo() -> int:\n    return 1\n"
        yield "pkg/bad.py", "def bad(:\n"

    monkeypatch.setattr(public_api, "iter_py_files_at_ref", fake_iter_py_files_at_ref)
    api = public_api.build_api_at_ref("HEAD", ["pkg"], [], ["_"])
    assert "good:foo" in api
    assert all("bad" not in key for key in api)
