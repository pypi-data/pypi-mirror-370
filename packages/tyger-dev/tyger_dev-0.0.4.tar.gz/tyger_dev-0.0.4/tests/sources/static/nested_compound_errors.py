x: int = 1
y: str = "hello"
z: bool = True

# Error in compound assignments 
a: tuple[int, str] = (y, x)  # TypeMismatchError (y is str, not int)
b: tuple[bool, int] = (z, y)  # TypeMismatchError (y is str, not int)
