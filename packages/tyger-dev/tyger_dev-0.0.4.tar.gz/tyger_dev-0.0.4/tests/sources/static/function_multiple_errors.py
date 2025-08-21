# Multiple errors in function parameters and returns
def foo(a: int) -> str:
    return a  # TypeMismatchError

def bar(b: str) -> bool:
    return b  # TypeMismatchError

def baz(c: bool) -> int:
    return c  # TypeMismatchError
