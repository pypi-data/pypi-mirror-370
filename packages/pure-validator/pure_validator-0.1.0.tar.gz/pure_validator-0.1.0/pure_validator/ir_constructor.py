import ast
import pathlib

from pure_validator.ir import (
    Loc,
    Module,
    Class,
    FunctionCall,
    FunctionReference,
    VariableReference,
)
from pure_validator.builtins import pure_builtins


class IRConstructor(ast.NodeVisitor):
    def __init__(self, path: pathlib.Path, source: str) -> None:
        super().__init__()
        self.source_lines = [""] + source.splitlines()
        self.path = path
        self.local_vars = set()
        self.args = {}
        self.module = Module(name=path.stem, path=path)
        self.current_class: Class | None = None
        self.current_function_ref: FunctionReference | None = None

    def get_or_create_variable_ref(self, name: str, node: ast.AST) -> VariableReference:
        return VariableReference(
            name=name,
            module=self.module,
            function=self.current_function_ref,
            class_=self.current_class,
            is_global=self.is_global(name, self.local_vars, self.args),
            loc=Loc.from_node(self.path, node),
        )

    def is_global(
        self, name: str, local_vars: set[str], args: dict[str, str | None]
    ) -> bool:
        if name in pure_builtins:
            return False
        return name not in local_vars and name not in args

    def is_pure_builtin(self, name: str) -> bool:
        return name in pure_builtins

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = self.module.get_or_create_class_ref(node.name)
        for stmt in node.body:
            self.visit(stmt)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_function_ref = self.current_function_ref
        old_local_vars = self.local_vars.copy()
        old_args = self.args.copy()
        self.local_vars = set()
        self.args = {arg.arg: None for arg in node.args.args}
        for arg in node.args.args:
            self.local_vars.add(arg.arg)
        self.current_function_ref = self.module.get_or_create_function_ref(
            node.name, self.current_class, Loc.from_node(self.path, node)
        )
        doc_string = ast.get_docstring(node)
        if doc_string and ("@pure" in doc_string or ":pure: true" in doc_string):
            self.current_function_ref.is_pure_marked = True
        for line in [node.lineno, node.lineno + 1]:
            if "# pragma: pure" in self.source_lines[line]:
                self.current_function_ref.is_pure_marked = True

        for stmt in node.body:
            self.visit(stmt)
        self.current_function_ref = old_function_ref
        self.local_vars = old_local_vars
        self.args = old_args

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            match target:
                case ast.Name() as name:
                    if self.current_function_ref:
                        self.local_vars.add(name.id)
                        var_ref = self.get_or_create_variable_ref(name.id, name)
                        if var_ref not in self.current_function_ref.variables:
                            self.current_function_ref.variables.append(var_ref)
                case ast.Attribute(ast.Name() as obj_name, attr="pure"):
                    func_ref = self.module.get_or_create_function_ref(
                        obj_name.id, self.current_class
                    )
                    func_ref.is_pure_marked = True
        self.visit(node.value)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            if (
                self.current_function_ref
                and not self.is_pure_builtin(node.id)
                and node.id not in self.module.functions
            ):
                var_ref = self.get_or_create_variable_ref(node.id, node)
                if var_ref not in self.current_function_ref.variables:
                    self.current_function_ref.variables.append(var_ref)

    def visit_Call(self, node: ast.Call) -> None:
        if self.current_function_ref:
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute) and isinstance(
                node.func.value, ast.Name
            ):
                func_name = f"{node.func.value.id}.{node.func.attr}"
            if func_name and not self.is_pure_builtin(func_name):
                called_func_ref = self.module.get_or_create_function_ref(func_name)
                func_call = FunctionCall(
                    function_ref=called_func_ref, loc=Loc.from_node(self.path, node)
                )
                if func_call not in self.current_function_ref.funcs:
                    self.current_function_ref.funcs.append(func_call)
        self.generic_visit(node)

    def visit_Global(self, node: ast.Global) -> None:
        for name in node.names:
            if self.current_function_ref:
                var_ref = self.get_or_create_variable_ref(name, node)
                var_ref.is_global = True
                if var_ref not in self.current_function_ref.variables:
                    self.current_function_ref.variables.append(var_ref)
