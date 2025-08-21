from tyger.discipline.base.types import unk


def foo(x: unk) -> int:
    y: bool = x
    return x + 1

foo(1)