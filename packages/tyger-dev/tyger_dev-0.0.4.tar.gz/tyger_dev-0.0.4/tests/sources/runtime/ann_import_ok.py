import tyger.discipline.simple.types as types


def foo(x: types.unk) -> types.unk:
    return baz(x)


def baz(x: int) -> int:
    return x

x = 1
y = foo(x)