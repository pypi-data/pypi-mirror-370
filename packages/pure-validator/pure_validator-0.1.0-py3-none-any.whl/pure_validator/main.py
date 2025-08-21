import ast
import tokenize
from pathlib import Path

from pure_validator.ir_constructor import IRConstructor
from pure_validator.message import Message
from pure_validator.purity_checker import PurityChecker


class PureError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def check_file(filename: str | Path) -> list[Message]:
    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Use tokenize.open() to handle different encodings, sometimes
    # specified as a leading '# -*- coding: utf-8 -*-' comment
    with tokenize.open(file_path) as f:
        source = f.read()

    # Pass 1: AST -> IR
    tree = ast.parse(source, filename=str(file_path))
    ir_constructor = IRConstructor(file_path, source=source)
    ir_constructor.visit(tree)
    module = ir_constructor.module

    # Pass 2: IR -> Purity Check
    purity_checker = PurityChecker(module)
    purity_checker.check()
    messages = purity_checker.messages

    return messages


def print_file_analysis(file_path: str | Path) -> None:
    file_path = Path(file_path)
    if file_path.is_dir():
        for sub_path in sorted(file_path.rglob("*.py")):
            # Skip hidden files and directories
            parts = sub_path.relative_to(file_path).parts
            if any(part.startswith(".") or part == "__pycache__" for part in parts):
                continue
            for msg in check_file(sub_path):
                print(msg)
    else:
        for msg in check_file(file_path):
            print(msg)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)

    print_file_analysis(sys.argv[1])
