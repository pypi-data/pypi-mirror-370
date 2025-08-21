x: int = 1
x: int = 2  # RedefineVariableError

y: bool = 3  # TypeMismatchError

z: str = "hello"
z: str = "hola"  # RedefineVariableError
