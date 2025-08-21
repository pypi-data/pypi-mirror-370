from typing import Callable

from tyger.discipline.base.types import unk

f: Callable[[unk], int] = lambda x,y: y
x = f(1,2)