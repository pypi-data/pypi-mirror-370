from tyger.discipline.base.types import unk
def foo(x: int) -> tuple[int,int]:
    return x, x+1

x: int
y: unk 
x,y = foo(4)

