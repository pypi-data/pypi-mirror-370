import typing
from typing import Union, Optional

# Test different import styles
def func_with_typing_union(x: typing.Union[int, str]) -> str:
    return "test"

def func_with_typing_optional(x: typing.Optional[str]) -> str:
    return "hello"

# Mixed Union and Optional with type errors
def func_with_mixed_annotations(x: Union[int, str], y: Optional[float]) -> int:
    a: str = 1  # Type mismatch error
    b: int = "hello"  # Type mismatch error
    return 42
