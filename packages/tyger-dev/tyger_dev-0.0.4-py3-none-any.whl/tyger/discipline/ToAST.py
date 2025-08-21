import ast
from abc import ABC, abstractmethod
from typing import cast

from tyger.discipline.evidence import Evidence, EvidenceFactory
from tyger.runtime.wrapper import ErrorLocation


class ASTElaborator(ABC):

    @abstractmethod
    def not_to_ast(self, node: ast.expr) -> ast.expr: ...

    @abstractmethod
    def bool_op_to_ast(self, op, values: list[ast.expr]) -> ast.expr: ...

    @abstractmethod
    def for_to_ast(self, target: ast.expr, iterable: ast.expr, body: list[ast.stmt], or_else: list[ast.stmt]) -> (
            list)[ast.stmt]: ...

    @abstractmethod
    def list_comp_to_ast(self, elt: ast.expr, generators: list[ast.comprehension], ifsp: ast.expr) -> ast.expr: ...

    @abstractmethod
    def list_comp_if_to_ast(self, ifp: ast.expr) -> ast.expr: ...

    @abstractmethod
    def unwrap_value_to_ast(self, node: ast.expr) -> ast.expr: ...

    @abstractmethod
    def type_to_ast(self, t: type) -> ast.AST:
        pass

    @abstractmethod
    def call_to_ast(self, func, argsp, keywords, *args):
        pass

    @abstractmethod
    def ite_to_ast(self, cond: ast.AST, then_branch: list[ast.AST], else_branch: list[ast.AST]) -> list[ast.AST]:
        pass

    @abstractmethod
    def assign_to_ast(self, targets, ty, value, context, prev_val=None) -> ast.AST:
        pass

    @abstractmethod
    def ann_assign_to_ast(self, target, annotation, ty, value, simple, context, prev_val=None) -> list[ast.AST]:
        pass

    @abstractmethod
    def return_to_ast(self, node: ast.AST, ev_expected: 'Evidence') -> list[ast.AST]:
        pass

    @abstractmethod
    def while_to_ast(self, cond: ast.expr, then_branch: list[ast.AST], orelse: list[ast.AST]) -> list[ast.AST]:
        pass

    @abstractmethod
    def evidence_to_ast(self, e: 'Evidence') -> ast.AST:
        pass

    @abstractmethod
    def cast_each_to_ast(self, ex, evidence): ...

    @abstractmethod
    def cast_elaborated(self, node: ast.AST, expected: type, loc: ErrorLocation = None) -> ast.AST: ...

    @abstractmethod
    def cast_each(self, valuep, target_type, vty): ...

    @abstractmethod
    def ev_fact_to_ast(self) -> ast.expr: ...

    @abstractmethod
    def import_to_ast(self, node: ast.Import): ...

    @abstractmethod
    def import_from_to_ast(self, node: ast.ImportFrom): ...

    @abstractmethod
    def evidence_import_to_ast(self):
        pass

    @abstractmethod
    def types_import_to_ast(self):
        pass

    @abstractmethod
    def runtime_import_to_ast(self):
        pass

    @abstractmethod
    def init_module_to_ast(self, module_name: str, module_src: str):
        pass


class BaseASTElaborator(ASTElaborator, ABC):

    def __init__(self, ev_fact: EvidenceFactory):
        self.n_loop = 0
        self.ev_fact = ev_fact

    def not_to_ast(self, node: ast.expr) -> ast.expr:
        return ast.Call(ast.Attribute(ast.Name('Wrapper', ast.Load()), '__not__', ast.Load()), [node], keywords=[])

    def bool_op_to_ast(self, op, values: list[ast.expr]) -> ast.expr:
        match op:
            case ast.And():
                return ast.Call(ast.Attribute(ast.Name('Wrapper', ast.Load()), '__land__', ast.Load()), values,
                                keywords=[])
            case ast.Or():
                return ast.Call(ast.Attribute(ast.Name('Wrapper', ast.Load()), '__lor__', ast.Load()), values,
                                keywords=[])
            case _:
                raise Exception(f"Unsupported operation: {op}")

    def for_to_ast(self, target: ast.Name, iterable: ast.expr, body: list[ast.stmt], orelse: list[ast.stmt]) -> (
            list)[ast.stmt]:
        self.n_loop += 1
        scope_name = f'__scope_{self.n_loop}'
        return [
            ast.With(
                items=[
                    ast.withitem(
                        context_expr=ast.Call(
                            func=ast.Name(id='LoopScope', ctx=ast.Load()),
                            args=[],
                            keywords=[]),
                        optional_vars=ast.Name(id=scope_name, ctx=ast.Store()))],
                body=[
                    ast.For(
                        target=target,
                        iter=iterable,
                        body=[ast.Expr(
                            ast.Call(func=ast.Attribute(value=ast.Name(id=scope_name, ctx=ast.Load()), attr='extract',
                                                        ctx=ast.Load()),
                                     args=[ast.Name(target.id, ctx=ast.Load())], keywords=[]))] + body,
                        orelse=orelse)])]

    def list_comp_to_ast(self, elt: ast.expr, generators: list[ast.comprehension], ifsp: ast.expr) -> ast.expr:
        if not ifsp:
            return ast.ListComp(elt, generators)
        else:
            elt = ast.Call(ast.Attribute(ast.Name('ComprehensionHelper', ast.Load()), 'for_yield', ast.Load()), [elt],
                           keywords=[])
            return ast.ListComp(elt, generators)

    def list_comp_if_to_ast(self, ifp: ast.expr) -> ast.expr:
        return ast.Call(ast.Attribute(ast.Name('ComprehensionHelper', ast.Load()), 'for_check', ast.Load()), [ifp],
                        keywords=[])

    def unwrap_value_to_ast(self, node: ast.expr) -> ast.expr:
        return ast.Call(ast.Attribute(ast.Name('Wrapper', ast.Load()), 'unwrap_value', ast.Load()), [node], keywords=[])

    def cast_elaborated(self, node: ast.AST, expected: type, loc: ErrorLocation = None) -> ast.AST:
        node_type = node.__type__
        context = node.__context__
        actual = node.__type__
        ev: Evidence = self.ev_fact.interior(actual, expected)
        node = self.cast_to_ast(node, ev, loc)
        node.__type__ = node_type
        node.__context__ = context
        return node

    def cast_to_ast(self, node: ast.AST, e: Evidence, loc: ErrorLocation = None) -> ast.expr:
        args = [node, self.evidence_to_ast(e)]
        if loc:
            args.append(ast.Constant(loc.lineno))
            args.append(ast.Constant(loc.col_offset))
        return ast.Call(ast.Name('Wrapper', ast.Load()), args=args, keywords=[])

    def cast_each(self, expr: ast.expr, to_type: tuple, from_type: type):
        evidence = self.ev_fact.each_interior(from_type, to_type)
        return self.cast_each_to_ast(expr, evidence)

    def cast_each_to_ast(self, expr: ast.expr, ev: tuple):
        return ast.Call(
            ast.Attribute(ast.Name("Wrapper", ast.Load()), "wrap_each", ast.Load()),
            [expr, self.each_ev_to_ast(ev)], []
        )

    def each_ev_to_ast(self, ev):
        match ev:
            case tuple():
                return ast.Tuple([self.each_ev_to_ast(in_ev) for in_ev in ev], ast.Load())
            case _:
                return self.evidence_to_ast(ev)

    def runtime_import_to_ast(self) -> list[ast.ImportFrom]:
        return [
            ast.ImportFrom("tyger.runtime.wrapper", [ast.alias("Wrapper")], 0),
            ast.ImportFrom("tyger.runtime.scopes", [ast.alias("*")], 0),
            ast.ImportFrom("tyger.runtime.custom_builtins", [ast.alias("Range")], 0),
            ast.ImportFrom("tyger.runtime.import_handler", [ast.alias("init_module")], 0)
        ]

    def import_to_ast(self, node: ast.Import):
        return [node]

    def import_from_to_ast(self, node: ast.ImportFrom):
        return [node]

    def init_module_to_ast(self, module_name: str, module_src: str):
        return [ast.Expr(ast.Call(ast.Name("init_module", ast.Load()),
                                  [ast.Constant(module_name), ast.Constant(module_src)], []))]
