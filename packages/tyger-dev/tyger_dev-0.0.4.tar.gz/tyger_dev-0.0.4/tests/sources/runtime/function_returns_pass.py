from typing import Callable

from tyger.discipline.base.types import unk


def baz(x: unk, y: unk) -> unk:
    pass
f: Callable[[int, bool], unk] = baz
x = f(10, True)