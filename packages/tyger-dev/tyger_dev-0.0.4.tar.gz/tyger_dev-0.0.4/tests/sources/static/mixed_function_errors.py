# Mixed errors in function bodies and outside
x: int = 1
x: int = 2  # RedefineVariableError

def func1(a: int) -> str:
    return 42  # TypeMismatchError

y: bool = "hello"  # TypeMismatchError

def func2(b: str) -> bool:
    c = 5
    c = True  # TypeMismatchError
    return True # Good
