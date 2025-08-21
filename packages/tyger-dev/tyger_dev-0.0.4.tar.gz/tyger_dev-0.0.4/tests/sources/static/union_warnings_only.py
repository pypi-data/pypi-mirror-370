from typing import Union

def func_with_union_param(x: Union[int, str]) -> str:
    return "test"

def func_with_union_return() -> Union[str, int]:
    return "hello"

# Nested Union types
def func_with_nested_union(x: Union[Union[int, str], float]) -> int:
    return 42
