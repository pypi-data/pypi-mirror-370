import module2.mod1 as imports
import imports.mod3

y = imports.x  # AttributeError: second import shadows first bound 'import' variable


