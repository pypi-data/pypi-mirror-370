import module.mod2
import module2.mod2  # This puts module.mod1 in scope

y = module.mod1.baz(module.mod2.x)


