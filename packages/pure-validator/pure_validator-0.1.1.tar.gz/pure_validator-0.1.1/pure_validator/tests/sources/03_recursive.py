def recursive_explicit(n: int) -> int:
    return n + recursive_explicit(1)


recursive_explicit.pure = True


def recursive_implicit(n: int) -> int:
    return n + recursive_implicit(1)
