from tyger.discipline.base.types import unk


def foo():
    return [1,2,"hola"]

x: int
y: unk
z: int

x,y,z = foo()