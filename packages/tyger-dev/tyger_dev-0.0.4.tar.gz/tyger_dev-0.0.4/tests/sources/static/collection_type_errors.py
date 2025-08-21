# Collection related type errors
a: list[int] = [1, 2, 3]
b: list[str] = a  # TypeMismatchError

c: dict[str, int] = {"x": 1, "y": 2}
d: dict[int, str] = c  # TypeMismatchError

e: tuple[int, str] = (1, "hello")
f: tuple[bool, int] = e  # TypeMismatchError
