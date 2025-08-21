import imports.submodule.mod1
import imports.mod5

z = imports.submodule.mod1.y
a = imports.submodule.mod1.imports2.mod1.foo(z)
b = imports.mod5.my_baz("Hola")