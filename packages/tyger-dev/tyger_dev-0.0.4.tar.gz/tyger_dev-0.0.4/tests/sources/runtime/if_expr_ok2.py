def foo(x: str) -> str:
    return x + "hola"

a = 1
b = 2
x = 3 if a > b else "hola"
res = foo(x)