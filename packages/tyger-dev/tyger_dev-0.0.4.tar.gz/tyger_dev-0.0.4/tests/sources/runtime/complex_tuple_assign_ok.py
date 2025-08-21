from tyger.discipline.base.types import unk


def foo() -> tuple[int, list[unk], bool]:
    return 1, [3, "hola"], True

x: int
y: str

x, (z,y), a = foo()