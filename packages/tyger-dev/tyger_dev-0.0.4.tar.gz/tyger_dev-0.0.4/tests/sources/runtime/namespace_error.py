import module.mod2
y = module.mod1.x  # AttributeError: mod1 is not in module's scope yet
import module2.mod1  # this import places mod1 in module's scope