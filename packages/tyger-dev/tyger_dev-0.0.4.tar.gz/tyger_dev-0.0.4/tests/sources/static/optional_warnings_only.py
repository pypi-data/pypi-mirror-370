from typing import Optional

def func_with_optional_param(x: Optional[int]) -> str:
    return "test"

def func_with_optional_return() -> Optional[str]:
    return "hello"

# Multiple Optional parameters
def func_with_multiple_optional(x: Optional[str], y: Optional[int]) -> Optional[bool]:
    return True
