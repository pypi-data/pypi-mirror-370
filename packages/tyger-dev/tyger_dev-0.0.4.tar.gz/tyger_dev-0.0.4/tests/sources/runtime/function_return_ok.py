from tyger.discipline.base.types import unk


def baz(x) -> unk:
    return 1
x: int = baz(1)
y = x+1