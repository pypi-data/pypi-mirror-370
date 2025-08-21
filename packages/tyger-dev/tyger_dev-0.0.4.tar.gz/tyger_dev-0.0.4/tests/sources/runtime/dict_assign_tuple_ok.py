def foo(): 
    return "hola", "chao"

def baz():
    return 1, foo()

d = {1: "a", 2: "b"}
x, [d[3], d[4]] = baz()