from typing import *

__all__ = ["datarepr"]


def datarepr(name: Any, /, *args: Any, **kwargs: Any) -> str:
    "This function allows for common sense representation."
    parts: list = list()
    x: Any
    for x in args:
        parts.append(repr(x))
    for x in kwargs.items():
        parts.append("%s=%r" % x)
    content: str = ", ".join(parts)
    ans: str = "%s(%s)" % (name, content)
    return ans
