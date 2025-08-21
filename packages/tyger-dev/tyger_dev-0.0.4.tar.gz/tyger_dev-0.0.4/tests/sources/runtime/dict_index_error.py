def foo():
    return 1

d = {"a":1, "b": 2} # type: dict[str,int]
x = foo() # type: unk
d[x] = 3 # TypeException