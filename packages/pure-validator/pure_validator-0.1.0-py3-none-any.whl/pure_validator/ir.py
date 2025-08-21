import ast
import dataclasses
import pathlib


@dataclasses.dataclass(frozen=True)
class Loc:
    """Stores source location information without keeping AST nodes."""

    path: pathlib.Path
    lineno: int | None = None
    col_offset: int | None = None
    end_lineno: int | None = None
    end_col_offset: int | None = None

    @classmethod
    def from_node(cls, path: pathlib.Path, node: ast.AST) -> "Loc":
        return cls(
            path=path,
            lineno=getattr(node, "lineno", None),
            col_offset=getattr(node, "col_offset", None),
            end_lineno=getattr(node, "end_lineno", None),
            end_col_offset=getattr(node, "end_col_offset", None),
        )

    def __str__(self) -> str:
        return f"{self.path}:{self.lineno or 0}:{self.col_offset or 0}"


@dataclasses.dataclass
class Module:
    name: str
    path: pathlib.Path
    functions: dict[str, "FunctionReference"] = dataclasses.field(default_factory=dict)
    classes: dict[str, "Class"] = dataclasses.field(default_factory=dict)

    def get_or_create_function_ref(
        self, name: str, class_: "Class | None" = None, location: Loc | None = None
    ) -> "FunctionReference":
        full_key = f"{class_.name}.{name}" if class_ else name
        if full_key not in self.functions:
            self.functions[full_key] = FunctionReference(
                name=name, module=self, class_=class_, loc=location
            )
        return self.functions[full_key]

    def get_or_create_class_ref(self, name: str) -> "Class":
        if name not in self.classes:
            self.classes[name] = Class(name=name, module=self)
        return self.classes[name]

    def should_check_function(
        self, name: str, current_class: "Class | None" = None
    ) -> bool:
        full_key = f"{current_class.name}.{name}" if current_class else name
        if full_key in self.functions:
            return self.functions[full_key].is_pure_marked
        return False


@dataclasses.dataclass(frozen=True)
class Class:
    name: str
    module: Module


@dataclasses.dataclass(frozen=True)
class FunctionCall:
    function_ref: "FunctionReference"
    loc: Loc


@dataclasses.dataclass
class FunctionReference:
    name: str
    module: Module
    class_: Class | None = None
    funcs: list["FunctionCall"] = dataclasses.field(default_factory=list)
    variables: list["VariableReference"] = dataclasses.field(default_factory=list)
    is_pure_marked: bool = False
    loc: Loc | None = None


@dataclasses.dataclass
class VariableReference:
    name: str
    module: Module
    function: FunctionReference | None = None
    class_: Class | None = None
    is_global: bool = False
    loc: Loc | None = None
