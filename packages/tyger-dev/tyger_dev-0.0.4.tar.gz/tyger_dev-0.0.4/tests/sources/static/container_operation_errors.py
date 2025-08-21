# More collection errors
d1: dict[str, int] = {"a": 1, "b": 2}
x = d1[5]  # TypeMismatchError - key is int, not str

d2 = {"a": 1, "b": 2}
d2["c"] = "hello"  # TypeMismatchError

lst: list[str] = ["a", "b", "c"]
i: str = lst[0]  # No error
j: int = lst[1]  # TypeMismatchError
