bad = 0


def prop_true(n: int) -> int:
    global bad
    return n


prop_true.pure = True


def doc_string(n: int) -> int:
    """
    @pure
    """
    global bad
    return n


def doc_string2(n: int) -> int:
    """
    :param n:
    :pure: true
    :return:
    """
    global bad
    return n


def comment_body(n: int) -> int:
    # pragma: pure
    global bad
    return n


def comment_before(n: int) -> int:  # pragma: pure
    global bad
    return n


# Expected:
# 5:4: Function 'prop_true' uses global variable 'bad'
# 16:4: Function 'doc_string' uses global variable 'bad'
# 26:4: Function 'doc_string2' uses global variable 'bad'
# 32:4: Function 'comment_body' uses global variable 'bad'
# 37:4: Function 'comment_before' uses global variable 'bad'
