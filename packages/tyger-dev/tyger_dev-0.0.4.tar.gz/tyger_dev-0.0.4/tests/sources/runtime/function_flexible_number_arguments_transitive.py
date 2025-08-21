from typing import Callable

from tyger.discipline.base.types import unk


def foo(x, y, z):
    return z

f: unk = foo
g: Callable[[unk], unk] = f
h: Callable[[unk, unk], unk] = g
x = g(2, 3, 4)