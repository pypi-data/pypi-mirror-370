# Import and attribute related errors
import module2.mod1

x = module2.mod1.baz(3)

y: dict[str, int] = {"a": "hola", "b": "hello"}  # TypeMismatchError

z: list[bool] = [1, 42]  # TypeMismatchError
