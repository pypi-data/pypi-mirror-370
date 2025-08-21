# Function call errors
def add(a: int, b: int) -> int:
    return a + b

x = add("hello", 5)  # TypeMismatchError
y = add(10, True)  # TypeMismatchError
