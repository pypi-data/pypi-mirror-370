from tyger.discipline.base.types import unk


def foo(x) -> dict[str, unk]:
    return {'x': x, 'y': 1}

d: dict[unk, int] = foo('3')

