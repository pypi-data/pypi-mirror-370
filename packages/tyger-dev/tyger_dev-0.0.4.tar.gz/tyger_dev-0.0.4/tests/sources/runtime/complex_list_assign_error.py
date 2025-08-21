def foo() -> tuple[int,int,int]:
    return (1,2,3)

def baz(): 
    return 1, foo(), 3

y: str
x, [y,z,a], b = baz()
