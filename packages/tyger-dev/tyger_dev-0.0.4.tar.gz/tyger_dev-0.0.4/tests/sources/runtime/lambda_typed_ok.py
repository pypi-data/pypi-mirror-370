from typing import Callable

from tyger.discipline.base.types import unk

f: Callable[[int, unk], int] = lambda x,y: x + y
x = f(1,2)