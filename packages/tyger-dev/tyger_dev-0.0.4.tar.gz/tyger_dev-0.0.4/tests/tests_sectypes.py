import unittest
from tyger.discipline.sectypes.ToAST import SecurityASTElaborator
from tyger.discipline.sectypes.types import SecurityTypeSystem, TypeException
from tyger.discipline.sectypes.evidence import RuntimeException
from tyger.runtime.wrapper import Wrapper
from tyger.phases.elaboration import ElaborationPhase
from tyger.phases.type_check import TypingPhase
from tyger.parser import Parser
from tyger.driver import Driver
import ast

class TestSectypes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = Parser()
        cls.driver = Driver([TypingPhase(SecurityTypeSystem()), ElaborationPhase(SecurityASTElaborator())])

    def execute(self, program: str):

        imports = """
from typing import Callable
from tyger.discipline.sectypes.types import H,M,L,unk,CodType
        """
        program = imports + program
        parsed_ast = self.parser.parse_string(program)
        #print(ast.dump(parsed_ast, indent=2))
        b, _ = self.driver.run(parsed_ast)

        #print(ast.dump(ast.fix_missing_locations(b), indent=2))
        scope = globals()
        print(ast.unparse(ast.fix_missing_locations(b)))
        exec(compile(ast.fix_missing_locations(b), filename="<ast>", mode="exec"), scope)
        return scope

    def nativeEquals(self, a, b):
        return self.assertEqual(Wrapper.unwrap_value(a), Wrapper.unwrap_value(b))

    def test_assignments_transitivity_fail(self):
        program = """
x: H = 1
z: unk = x
y: L = z
print(y)
        """
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_binop1(self):
        program = """    
x: H = 1
y: L = 2
z: unk = x + y
w: H = z
        """

        self.nativeEquals(3, self.execute(program)['w'])
    def test_binop2(self):
        program = """    
x: H = 1
y: L = 2
z: unk = x + y
w: L = z
        """

        self.assertRaises(RuntimeException, lambda: self.execute(program))


    def test_taint1(self):
        program = """    
x: H = 1
y: L = x > 2
        """

        self.assertRaises(TypeException, lambda: self.execute(program))

    def test_taint2(self):
        program = """    
def foo():
    x: H = 1
    if x < 2:
        return 1
        
z: L = foo()
print(z)
        """

        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_taint3(self):
        program = """    
def foo(x: L) -> H:
    return x

z: unk = foo(1)
z: L = z
print(z)
            """

        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_func(self):
        program = """    
def foo(x: L) -> CodType[H,H,H]:
    return x

z: unk = foo(1)
z: L = z
print(z)
            """

        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_if_join_error(self):
        program = """    
def foo() -> L:
    x: H = 1
    if x < 10:
        return 1 
        """

        self.assertRaises(TypeException, lambda: self.execute(program))

    def test_if_join_ok(self):
        program = """    
def foo() -> H:
    x: H = 1
    if x < 10:
        return 1
x = foo()
        """

        self.nativeEquals(1, self.execute(program)['x'])

    def test_references_and_pc1_error(self):
        program = """
x: H = 1
if x < 10:
    y: L = 1
        """

        self.assertRaises(TypeException, lambda: self.execute(program))

    def test_references_and_pc1_ok(self):
        program = """
x: H = 1
if x < 10:
    y: H = 1
        """

        self.nativeEquals(1, self.execute(program)['y'])

    def test_references_and_pc2_error(self):
        program = """
x: H = 1
y: unk = 1
if x < 10:
    y = 2
        """

        self.assertRaises(RuntimeException, lambda: self.execute(program))



    def test_hofunction_ok(self):
        program = """    
def baz(x: unk, y: unk) -> unk:
    return y
f: Callable[[H, L], CodType[L,L,L]] = baz
y: H = 10
z: L = True
x = f(y, z)
        """

        self.nativeEquals(True, self.execute(program)['x'])

    def test_hofunction_error(self):
        program = """    
def baz(x: unk, y: L) -> unk:
    return y
f: Callable[[H, unk], CodType[L,L,L]] = baz
print(f)
y: H = 10
z: H = True
x = f(y, z)
        """

        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_unknown_application(self):
        program = """
def baz(x: unk, y: L) -> unk:
    return y
f: unk = baz
x = f(10, True)
        """
        self.nativeEquals(True, self.execute(program)['x'])

    def test_lambda_typed_ok(self):
        program = """
f: Callable[[L, L], CodType[L, L, L]] = lambda x,y: x + y
x = f(1,2)
        """
        self.nativeEquals(3, self.execute(program)['x'])

    def test_lambda_typed_error(self):
        program = """
f: Callable[[L, unk], CodType[L, L, L]] = lambda x,y: x + y
y: H = True
x = f(1, y)
        """
        self.assertRaises(RuntimeException, lambda: self.execute(program))


    def test_lambda_modular_not_forgetful(self):
        program = """
f: Callable[[unk, unk], unk]  = lambda x,y: x + y
g: Callable[[L, H], CodType[L, L, H]] = f
h: Callable[[unk, unk], unk] = g
i: Callable[[H, H], CodType[L, L, L]] = h

x = i(1, 2)
print(x)
        """

        self.assertRaises(RuntimeException, lambda: self.execute(program))


    def test_example_1_1(self):
        program = """
x: L = 10
b1: H = True
b2: unk = b1
if b2:  
    x: L = 20
        """

        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_example_nsu_fennel_etal_ok(self):
        program = """
x: L = True
x_p: unk = x
y: L = True
y_pp: unk = y
z: L = True
z_p: unk = z
if x_p:  
    y_p: L = False
if y_p:
    z_p: L = False
print(z_p)
        """
        self.nativeEquals(True, Wrapper.unwrap_value(self.execute(program)['z_p']))


    def test_example_nsu_fennel_etal_error(self):
        program = """
x: H = True
x_p: unk = x
y: L = True
y_pp: unk = y
z: L = True
z_p: unk = z
if x_p:  
    y_p: L = False
if y_p:
    z_p: L = False
print(z_p)
        """
        self.assertRaises(RuntimeException, lambda: self.execute(program))

    def test_implicit_flow_runtime(self):
        #this program should fail as the evidence of the pc should be <H,H>, and the expected type is <L,L>
        program = """
def foo() -> L:
    y: H = 10
    x: unk = y
    if x < 20:
        return 1
"""
        self.assertRaises(RuntimeException, lambda: self.execute(program))
