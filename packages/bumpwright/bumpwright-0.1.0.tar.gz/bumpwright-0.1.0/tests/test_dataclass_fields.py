from bumpwright.compare import Impact, diff_public_api
from bumpwright.public_api import extract_public_api_from_source

MAJOR = "major"
MINOR = "minor"


def test_dataclass_field_addition_detected() -> None:
    old_code = """
from dataclasses import dataclass

@dataclass
class Foo:
    x: int
"""
    new_code = """
from dataclasses import dataclass

@dataclass
class Foo:
    x: int
    y: int
"""
    old = extract_public_api_from_source("m", old_code)
    new = extract_public_api_from_source("m", new_code)
    impacts = diff_public_api(old, new)
    assert Impact(MAJOR, "m:Foo.__init__", "Added required param 'y'") in impacts


def test_dataclass_field_removal_detected() -> None:
    old_code = """
from dataclasses import dataclass

@dataclass
class Foo:
    x: int
    y: int
"""
    new_code = """
from dataclasses import dataclass

@dataclass
class Foo:
    x: int
"""
    old = extract_public_api_from_source("m", old_code)
    new = extract_public_api_from_source("m", new_code)
    impacts = diff_public_api(old, new)
    assert Impact(MAJOR, "m:Foo.__init__", "Removed required param 'y'") in impacts


def test_dataclass_field_default_changes_detected() -> None:
    old_code = """
from dataclasses import dataclass

@dataclass
class Foo:
    x: int = 1
    y: int
    z: int = 1
"""
    new_code = """
from dataclasses import dataclass

@dataclass
class Foo:
    x: int
    y: int = 2
    z: int = 2
"""
    old = extract_public_api_from_source("m", old_code)
    new = extract_public_api_from_source("m", new_code)
    impacts = diff_public_api(old, new)
    assert Impact(MAJOR, "m:Foo.__init__", "Param 'x' default removed") in impacts
    assert Impact(MINOR, "m:Foo.__init__", "Param 'y' default added") in impacts
    assert Impact(MINOR, "m:Foo.__init__", "Param 'z' default changed 1→2") in impacts
