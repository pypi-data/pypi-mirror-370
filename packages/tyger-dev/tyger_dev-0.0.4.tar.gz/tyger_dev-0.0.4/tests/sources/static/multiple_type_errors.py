# Three TypeMismatchError instances
x: int = 42
y: bool = x  # Error 1

a: str = "hello"
b: int = a  # Error 2

c: bool = True
d: str = c  # Error 3
