import dataclasses
import pathlib


@dataclasses.dataclass
class Message:
    message: str
    path: pathlib.Path
    lineno: int | None = None
    col_offset: int | None = None

    def __str__(self) -> str:
        return f"{self.path}:{self.lineno}:{self.col_offset}: {self.message}"
