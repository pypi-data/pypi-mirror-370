from tyger.discipline.base.types import unk


def foo(x: unk) -> int:
    if x:
        return 1
    else:
        return 2  
x = foo(False)