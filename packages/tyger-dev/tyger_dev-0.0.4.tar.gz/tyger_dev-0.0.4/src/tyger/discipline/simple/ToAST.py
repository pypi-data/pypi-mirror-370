from typing import Callable, get_args
import ast
import builtins
from tyger.discipline.ToAST import BaseASTElaborator
from tyger.discipline.base.types import TypeName
from tyger.discipline.evidence import Evidence
from tyger.discipline.simple.evidence import simple_factory


def render_unwrap(target):
    return ast.Call(
        ast.Attribute(ast.Name("Wrapper", ast.Load()), "unwrap_value", ast.Load()),
        [target], []
    )


class SimpleASTElaborator(BaseASTElaborator):

    def __init__(self):
        super().__init__(simple_factory)
        self.n_loop = 0

    def type_to_ast(self, t: type) -> ast.AST:
        match t.__qualname__:
            case Callable.__qualname__:
                dom, cod = get_args(t)
                args = [self.type_to_ast(a) for a in dom]
                ret = self.type_to_ast(cod)
                return ast.Subscript(ast.Name('Callable', ast.Load()),
                                     ast.Tuple(elts=[ast.List(elts=args, ctx=ast.Load()), ret], ctx=ast.Load()),
                                     ast.Load())
            case tuple.__qualname__:
                args = get_args(t)
                return ast.Subscript(ast.Name('tuple', ast.Load()),
                                     ast.Tuple(elts=[self.type_to_ast(a) for a in args], ctx=ast.Load()),
                                     ast.Load())
            case list.__qualname__:
                args = get_args(t)
                return ast.Subscript(ast.Name('list', ast.Load()),
                                     ast.Tuple(elts=[self.type_to_ast(a) for a in args], ctx=ast.Load()),
                                     ast.Load())
            case dict.__qualname__:
                dom, cod = get_args(t)
                return ast.Subscript(ast.Name('dict', ast.Load()),
                                     ast.Tuple(elts=[self.type_to_ast(dom), self.type_to_ast(cod)], ctx=ast.Load()),
                                     ast.Load())


            case TypeName.__qualname__:
                # TypeName("")
                return ast.Call(ast.Name(id='TypeName', ctx=ast.Load()), [ast.Constant(value=t.name)], [])
            case _:
                return ast.Name(t.__qualname__, ast.Load())

    def call_to_ast(self, func, argsp, keywords, *args):

        # For builtin functions, we need to unwrap the arguments. 
        # As builtins have type unk, we need to check if func is a call to Wrapper and if its 

        if isinstance(func, ast.Name) and hasattr(builtins, func.id):
            argsp = [render_unwrap(argg) for argg in argsp]
        return ast.Call(func, argsp, keywords)

    def ite_to_ast(self, cond: ast.AST, then_branch: list[ast.AST], else_branch: list[ast.AST]) -> list[ast.AST]:
        return [ast.If(
            ast.Call(ast.Attribute(ast.Name('Wrapper', ast.Load()), 'unwrap_value', ast.Load()), [cond], keywords=[]),
            then_branch,
            else_branch)]

    def assign_to_ast(self, targets, ty, value, *args) -> list[ast.AST]:
        return [ast.Assign(targets, value)]

        # ev_expected = interior(ty, ty)
        # valuep = Call(
        #    func=Attribute(
        #        value=Name(id='Wrapper', ctx=Load()),
        #        attr='intercept_assign',
        #        ctx=Load()),
        #    args=[value, evidence_to_ast(ev_expected)] if ev_expected else [value],
        #    keywords=[])
        #
        # return [Assign(targets, valuep)]

    def ann_assign_to_ast(self, target, annotation, ty, value, simple, context, prev_value) -> list[ast.AST]:
        return [ast.AnnAssign(target, annotation, value, simple)]
        # valuep = Call(
        #    func=Attribute(
        #        value=Name(id='Wrapper', ctx=Load()),
        #        attr='intercept_assign',
        #        ctx=Load()),
        #    args=[value],
        #    keywords=[])
        # return [AnnAssign(target, annotation, valuep, simple)]

    def return_to_ast(self, node: ast.AST, ev_expected: Evidence | None = None) -> list[ast.AST]:
        return [ast.Return(node)]

    # TODO: orelse?
    def while_to_ast(self, cond: ast.Expr, then_branch: list[ast.AST], orelse: list[ast.AST]) -> list[ast.AST]:
        return [ast.While(
            test=ast.Call(ast.Attribute(ast.Name('Wrapper', ast.Load()), 'unwrap_value', ast.Load()), [cond],
                          keywords=[]),
            body=then_branch,
            orelse=orelse)]

    def evidence_to_ast(self, e: Evidence) -> ast.AST:
        return ast.Call(ast.Name('SimpleEvidence', ast.Load()), [self.type_to_ast(e.l), self.type_to_ast(e.r)],
                        keywords=[])

    def ifexp_to_ast(self, test: ast.Expr, body: ast.Expr, orelse: ast.Expr) -> ast.AST:
        return ast.IfExp(
            ast.Call(ast.Attribute(ast.Name("Wrapper", ast.Load()), "unwrap_value", ast.Load()), [test], []),
            body, orelse
        )

    def ev_fact_to_ast(self):
        return ast.Name("simple_factory", ast.Name())

    def evidence_import_to_ast(self):
        return ast.ImportFrom("tyger.discipline.simple.evidence",
                              [ast.alias("SimpleEvidence"), ast.alias("simple_factory")], 0)

    def types_import_to_ast(self):
        type_imports = [
            ast.ImportFrom("typing", [ast.alias("Callable")], 0),
            ast.ImportFrom("tyger.discipline.simple.types", [ast.alias("unk"), ast.alias("tslice")], 0),
        ]
        return type_imports
