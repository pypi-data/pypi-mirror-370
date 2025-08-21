# 2 RedefineVariableError and 2 TypeMismatchError
x: int = 1
x: int = 2  # RedefineVariableError

y: bool = 3  # TypeMismatchError

z: str = "hello"
z: str = "world"  # RedefineVariableError

w = True
w = "test"  # TypeMismatchError
