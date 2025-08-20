from typing import Any


def is_namedtuple_type(x: Any) -> bool:
    if not hasattr(x, "__annotations__"):
        return False

    if not hasattr(x, "__bases__"):
        return False

    b = x.__bases__
    if len(b) != 1 or b[0] is not tuple:
        return False
    return all(isinstance(n, str) for n in x._fields)
