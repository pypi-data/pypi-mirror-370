from tyger.discipline.base.types import unk

x: unk = True
l: list[tuple[int,int]] = [(x,y) for x in range(x) for y in range(4) if y<x]