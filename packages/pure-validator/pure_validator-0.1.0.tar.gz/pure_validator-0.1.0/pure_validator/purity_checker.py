from pure_validator.builtins import pure_builtins
from pure_validator.ir import Loc, Module, FunctionCall, FunctionReference, VariableReference
from pure_validator.message import Message


class PurityChecker:
    def __init__(self, module: Module):
        self.module = module
        self.messages: list[Message] = []
        self.visited_functions: set[str] = set()
        self.pure_functions: set[str] = set()
        self.call_stack: set[str] = set()

    def is_pure_builtin(self, name: str) -> bool:
        return name in pure_builtins

    def append_message(self, *, location: Loc, message: str) -> None:
        self.messages.append(
            Message(
                message=message,
                path=location.path,
                lineno=location.lineno,
                col_offset=location.col_offset,
            )
        )

    def get_function_key(self, func_ref: FunctionReference) -> str:
        return (
            f"{func_ref.class_.name}.{func_ref.name}"
            if func_ref.class_
            else func_ref.name
        )

    def check_function_purity(self, func_ref: FunctionReference) -> bool:
        func_key = self.get_function_key(func_ref)
        if func_key in self.call_stack:
            return func_ref.is_pure_marked
        if func_key in self.visited_functions:
            return func_key in self.pure_functions
        self.visited_functions.add(func_key)
        self.call_stack.add(func_key)

        try:
            is_pure = self._analyze_function_purity(func_ref)
            if is_pure:
                self.pure_functions.add(func_key)
            return is_pure
        finally:
            self.call_stack.remove(func_key)

    def _analyze_function_purity(self, func_ref: FunctionReference) -> bool:
        return self._check_function_calls(func_ref) and self._check_global_variables(
            func_ref
        )

    def _check_function_calls(self, func_ref: FunctionReference) -> bool:
        for func_call in func_ref.funcs:
            if not self._is_function_call_pure(func_ref, func_call):
                return False
        return True

    def _is_function_call_pure(
        self, caller: FunctionReference, func_call: FunctionCall
    ) -> bool:
        called_func = func_call.function_ref
        called_key = self.get_function_key(called_func)
        if self.is_pure_builtin(called_func.name):
            return True
        if not called_func.is_pure_marked and called_key not in self.module.functions:
            self._report_impure_call(caller, func_call, "impure function")
            return False
        if called_func.is_pure_marked:
            if not self.check_function_purity(called_func):
                self._report_impure_call(caller, func_call, "impure function")
                return False
        else:
            self._report_impure_call(caller, func_call, "non-pure function")
            return False
        return True

    def _check_global_variables(self, func_ref: FunctionReference) -> bool:
        for var_ref in func_ref.variables:
            if self.is_pure_builtin(var_ref.name) or not var_ref.is_global:
                continue
            self._report_global_variable_usage(func_ref, var_ref)
            return False
        return True

    def _report_impure_call(
        self, caller: FunctionReference, func_call: FunctionCall, reason: str
    ) -> None:
        if func_call.loc:
            self.append_message(
                location=func_call.loc,
                message=f"Function '{caller.name}' calls {reason} '{func_call.function_ref.name}'",
            )

    def _report_global_variable_usage(
        self, func_ref: FunctionReference, var_ref: VariableReference
    ) -> None:
        if var_ref.loc:
            self.append_message(
                location=var_ref.loc,
                message=f"Function '{func_ref.name}' uses global variable '{var_ref.name}'",
            )

    def check(self) -> None:
        for func_name, func_ref in self.module.functions.items():
            if func_ref.is_pure_marked:
                self.check_function_purity(func_ref)
