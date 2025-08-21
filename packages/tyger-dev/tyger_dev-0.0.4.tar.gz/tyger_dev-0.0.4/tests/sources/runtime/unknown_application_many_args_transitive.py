from typing import Callable

from tyger.discipline.base.types import unk


def foo(x, y, z):
    return z
f: Callable[[unk, unk, bool], unk] = foo
g: unk = f
x = g(2, 3, 4)