# Nested function errors
def outer() -> int:
    def inner(x: bool) -> str:
        y: int = x  # TypeMismatchError
        return 42  # TypeMismatchError
        
    z: str = inner(True)
    return z  # TypeMismatchError
