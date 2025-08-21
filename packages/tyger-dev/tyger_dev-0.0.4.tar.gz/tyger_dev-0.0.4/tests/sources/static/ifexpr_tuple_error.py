from tyger.discipline.base.types import unk

def foo() -> tuple[unk, int]:
    return (2,1)

def baz() -> tuple[int, int]:
    return (3,1)

x = foo() if 2 > 3 else baz()
x = (2,"hola")