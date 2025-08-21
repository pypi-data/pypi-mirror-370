# More complex return type errors
def func1() -> tuple[int, str]:
    return (True, 42)  # TypeMismatchError

def func2() -> dict[str, int]:
    return {"a": "hello", "b": "hola"}  # TypeMismatchError

def func3() -> list[bool]:
    return [1, 2, 3]  # TypeMismatchError
