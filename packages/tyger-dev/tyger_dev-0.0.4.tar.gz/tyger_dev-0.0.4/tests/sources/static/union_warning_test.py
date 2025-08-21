from typing import Union, Optional

# Union and Optional should emit warnings but not crash
def test_union_warning(x: Union[int, str]) -> int:
    return 42

def test_optional_warning(x: Optional[str]) -> str:
    return "hello"

# Regular type errors should still be caught
def test_regular_error() -> None:
    a: str = 1  # This should still cause a type error
    return None
