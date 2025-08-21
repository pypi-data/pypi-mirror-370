from tyger.discipline.base.types import unk
def foo():
    print("1")
    return 1

x: int
y: unk
x = y = foo()