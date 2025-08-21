name: str = "Juan"
age: int = 30
height: float = 5.6

message: str = f"Hello, {name}!"
info: str = f"Name: {name}, Age: {age}, Height: {height}"

# F-string with format specifiers
formatted: str = f"Age: {age:d}, Height: {height:.1f}"
calculation: str = f"Next year, {name} will be {age + 1} years old"
