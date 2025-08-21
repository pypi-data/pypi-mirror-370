from typing import Callable
from tyger.discipline.base.types import unk

f: Callable[[int, int, unk], int] = lambda x,y,z: x
g: Callable[[int], int] = lambda z: z

f = g