from typing import Callable

from tyger.discipline.base.types import unk

f: Callable[[unk, unk], unk] = lambda x,y: x + y
g: Callable[[int, bool], int] = f
h: Callable[[unk, unk], unk] = g
i: Callable[[int, int], int] = h

x = i(1, 2)
print(x)