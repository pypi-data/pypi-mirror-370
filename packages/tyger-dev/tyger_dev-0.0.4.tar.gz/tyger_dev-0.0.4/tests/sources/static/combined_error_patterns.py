# Combination of error patterns
# Variable redefinitions
a: int = 1
a: int = 3  # RedefineVariableError

# Type mismatches in variables
b: bool = 42  # TypeMismatchError
c: str = True  # TypeMismatchError

# Dictionary errors
a: dict[str,int] = {"a": 1, "b": 2, "c": 3}
a[4] = 4 # TypeMismatchError

# Function errors
def func(x: int) -> bool:
    y: str = x  # TypeMismatchError
    return "result"  # TypeMismatchError
