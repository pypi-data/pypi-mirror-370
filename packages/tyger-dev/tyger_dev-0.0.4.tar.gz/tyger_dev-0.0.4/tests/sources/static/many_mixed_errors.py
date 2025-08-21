# Mix of different error types
# Error 1 - RedefineVariableError
a: int = 1
a: int = 2


# Error 2 - TypeMismatchError
def func(x: str) -> bool:
    return x


func("hello")

# Error 3 - TypeMismatchError
b: dict[str, int] = {"name": "John"}

# Error 4 - RedefineVariableError
c: bool = True
c: int = 42

# Error 5 - TypeMismatchError
d: list[str] = [1, 1, 1]

# Error 6 - TypeMismatchError
e: int = "world"
