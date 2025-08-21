# Five TypeMismatchErrors
x: int = 42
y: str = x  # Error 1

a: bool = True
b: int = a  # Error 2

c: int = 21
d: bool = c  # Error 3

e: str = "hello"
f: int = e  # Error 4

g: str = "world"
h: int = g  # Error 5
