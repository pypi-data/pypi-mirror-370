global_var: int = 10


def impure_func() -> None:
    global global_var
    global_var += 1


def pure_func(i: int) -> int:
    return i + 1


pure_func.pure = True  # auto-detected pure function?


def f(n: int) -> int:
    x = False
    y = True
    z = None
    y = global_var
    pure_func(10)
    impure_func()
    return f(1)


f.pure = True

# Expected:
# 22:4: Function 'f' calls non-pure function 'impure_func'
