from typing import Callable

f: Callable[[Callable[[int], int]], int] = lambda f: f("hola")
x = f(lambda y: y)