import functools
from typing import *

__all__ = [
    "classdecorator",
    "getdecorator",
    "getproperty",
]


def classdecorator(cls: Any, /, **kwargs: Any) -> Any:
    "This decorator adds keyaliases to cls and then returns cls."
    alias: str
    key: Any
    pro: property
    for alias, key in kwargs.items():
        pro = getproperty(key)
        setattr(cls, alias, pro)
    return cls


def getdecorator(**kwargs: Any) -> functools.partial:
    "This function returns a keyalias decorator for a class."
    return functools.partial(classdecorator, **kwargs)


def getproperty(key: Any) -> property:
    "This function returns a new keyalias property."

    def fget(self: Self, /) -> Any:
        return self[key]

    def fset(self: Self, value: Any, /) -> Any:
        self[key] = value

    def fdel(self: Self, /) -> Any:
        del self[key]

    doc: str = "self[%r]" % key
    ans: property = property(fget, fset, fdel, doc)
    return ans
