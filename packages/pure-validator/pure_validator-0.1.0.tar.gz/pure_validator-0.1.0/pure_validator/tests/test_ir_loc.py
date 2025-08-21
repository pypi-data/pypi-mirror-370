#!/usr/bin/env python3
"""Test the SourceLocation.from_node class method."""

import ast
from pathlib import Path

from pure_validator.ir import Loc


def parse(source: str) -> Loc:
    tree = ast.parse(source, filename="test.py")
    location = Loc.from_node(Path("test.py"), tree.body[0])
    return location


def test_loc_from_node() -> None:
    loc = parse("""def hello():
    print("Hello, world!")
""")
    assert loc.path == Path("test.py")
    assert loc.lineno == 1
    assert loc.col_offset == 0
    assert loc.end_lineno == 2
    assert loc.end_col_offset == 26
