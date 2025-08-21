from tyger.discipline.base.types import unk
def foo(x: int) -> tuple[int,unk]:
    return x, x+1

x: int
y: str
x,y = foo(5)

