# imports.mod5 imports imports.submodule.mod5, then submodule should be in imports namespace
import imports.mod5

z = imports.mod5.my_baz(7)
a = imports.submodule.mod5.baz(4)

