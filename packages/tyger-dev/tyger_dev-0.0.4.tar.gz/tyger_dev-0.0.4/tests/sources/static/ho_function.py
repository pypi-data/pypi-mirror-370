from typing import Callable


def bar(f: Callable[[int], bool]):
    pass
def baz(x: bool)-> bool:
    pass
bar(baz)  