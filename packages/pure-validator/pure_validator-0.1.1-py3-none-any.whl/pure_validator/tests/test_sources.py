import pathlib
import tokenize

import pytest

from pure_validator.main import check_file
from pure_validator.message import Message

sources_dir = pathlib.Path(__file__).parent / "sources"


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "path" in metafunc.fixturenames:
        test_files = sorted(sources_dir.glob("*.py"))
        metafunc.parametrize("path", test_files, ids=[f.stem for f in test_files])


def parse_expected_message(source: str, path: pathlib.Path) -> list[Message]:
    lines = source.splitlines()
    messages: list[Message] = []
    header = False
    for lineno, line in enumerate(lines, start=1):
        if line == "# Expected:":
            header = True
            continue
        if header:
            lineno, col_offset, message = line[2:].split(":", 3)
            messages.append(
                Message(
                    message=message[1:],
                    path=path,
                    lineno=int(lineno),
                    col_offset=int(col_offset),
                )
            )

    return messages


def test_source(path: pathlib.Path) -> None:
    with tokenize.open(path) as f:
        source = f.read()

    expected_messages = parse_expected_message(source, path=path)
    actual_messages = check_file(path)
    assert list(map(str, actual_messages)) == list(map(str, expected_messages))
