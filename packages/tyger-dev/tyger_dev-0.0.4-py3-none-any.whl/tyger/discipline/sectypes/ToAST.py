import ast
from typing import Callable, get_args

from tyger.discipline.ToAST import BaseASTElaborator
from tyger.discipline.evidence import Evidence
from tyger.discipline.sectypes.evidence import security_factory, TUnk, TBool, TInt, TCallable, interval, T, E, \
    interior_i, interval_bounds, SecurityEvidence
from tyger.discipline.sectypes.types import extract_func_type, extract_cod_lbl_lat, extract_lbl
from tyger.discipline.types import Context


class SecurityASTElaborator(BaseASTElaborator):

    def __init__(self):
        super().__init__(security_factory)

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
            case _:
                return ast.Name(t.__qualname__, ast.Load())

    def call_to_ast(self, func, argsp, keywords, context: Context, ty: Callable):
        dom, cod = extract_func_type(ty)
        cod, lbl, lat = extract_cod_lbl_lat(cod)
        i1, i2 = interior_i(interval_bounds(context.pc).join(interval_bounds(lbl)), interval_bounds(lat))
        ev3 = SecurityEvidence(E(TUnk(), i1), E(TUnk(), i2))
        ev1 = self.ev_fact.interior(ty, ty)
        return ast.Call(ast.Name("custom_call", ast.Load()),
                        [func, self.evidence_to_ast(ev3), self.evidence_to_ast(ev1), *argsp], keywords)

    def ite_to_ast(self, cond: ast.AST, then_branch: list[ast.AST], else_branch: list[ast.AST]) -> list[ast.AST]:
        return [
            ast.With(
                items=[
                    ast.withitem(
                        context_expr=ast.Call(
                            func=ast.Name(id='ConditionalScope', ctx=ast.Load()),
                            args=[cond],
                            keywords=[]),
                        optional_vars=ast.Name(id='__val', ctx=ast.Store()))],
                body=[
                    ast.If(
                        test=ast.Name(id='__val', ctx=ast.Load()),
                        body=then_branch,
                        orelse=else_branch)])]

    def assign_to_ast(self, targets, ty, value, context, prev_val=None) -> ast.AST:
        ev_expected = self.ev_fact.interior(ty, ty)
        ev_pc = self.ev_fact.interior(context.pc, extract_lbl(ty))
        args = [value]
        args.append(self.evidence_to_ast(ev_expected)) if ev_expected else args.append(ast.Constant(None))
        args.append(self.evidence_to_ast(ev_pc))
        if prev_val:
            args.append(prev_val)

        valuep = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='Wrapper', ctx=ast.Load()),
                attr='intercept_assign',
                ctx=ast.Load()),
            args=args,
            keywords=[])

        return [ast.Assign(targets, valuep)]

    def ann_assign_to_ast(self, target, annotation, ty, value, simple, context, prev_val=None) -> list[ast.AST]:

        # print(target, annotation, ty, value, simple, ev_expected, context)
        ev_pc = self.ev_fact.interior(context.pc, extract_lbl(ty))
        args = [value, ast.Constant(None), self.evidence_to_ast(ev_pc)]
        # args.append(evidence_to_ast(ev_expected)) if ev_expected else (
        if prev_val:
            args.append(prev_val)
        valuep = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='Wrapper', ctx=ast.Load()),
                attr='intercept_assign',
                ctx=ast.Load()),
            args=args,
            keywords=[])

        return [ast.AnnAssign(target, annotation, valuep, simple)]

    def return_to_ast(self, node: ast.AST, ev_expected: Evidence | None = None) -> list[ast.AST]:
        return [ast.Return(ast.Call(
            func=ast.Attribute(
                value=ast.Name(id='Wrapper', ctx=ast.Load()),
                attr='intercept_return',
                ctx=ast.Load()),
            args=[node, self.evidence_to_ast(ev_expected)] if ev_expected else [node],
            keywords=[]))]

    # TODO: orelse?
    n_loop: int = 0

    def while_to_ast(self, cond: ast.Expr, then_branch: list[ast.AST], orelse: list[ast.AST]) -> list[ast.AST]:
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
                    ast.While(
                        test=ast.Call(func=ast.Attribute(value=ast.Name(id=scope_name, ctx=ast.Load()), attr='extract',
                                                         ctx=ast.Load()),
                                      args=[cond], keywords=[]),
                        body=then_branch,
                        orelse=orelse)])]

    def interval_to_ast(self, i: interval) -> ast.AST:
        return ast.Call(ast.Name('interval', ast.Load()), [self.type_to_ast(i.l), self.type_to_ast(i.r)], keywords=[])

    def T_to_ast(self, t: T) -> ast.AST:
        match t:
            case TUnk():
                return ast.Call(ast.Name('TUnk', ast.Load()), [], keywords=[])
            case TBool():
                return ast.Call(ast.Name('TBool', ast.Load()), [], keywords=[])
            case TInt():
                return ast.Call(ast.Name('TInt', ast.Load()), [], keywords=[])
            case TCallable():
                args = [self.E_to_ast(a) for a in t.dom]
                cod = self.E_to_ast(t.cod)
                lat = self.interval_to_ast(t.lat)
                return ast.Call(ast.Name('TCallable', ast.Load()), [ast.List(args, ast.Load()), cod, lat], keywords=[])
            case _:
                raise Exception(f"Not implemented T_to_ast({t})")

    def E_to_ast(self, e: E) -> ast.AST:
        return ast.Call(ast.Name('E', ast.Load()), [self.T_to_ast(e.ty), self.interval_to_ast(e.i)], keywords=[])

    def evidence_to_ast(self, e: Evidence) -> ast.AST:
        return ast.Call(ast.Name('SecurityEvidence', ast.Load()), [self.E_to_ast(e.l), self.E_to_ast(e.r)],
                        keywords=[])

    def ev_fact_to_ast(self) -> ast.expr:
        return ast.Name("security_factory", ast.Load())

    def evidence_import_to_ast(self):
        return ast.ImportFrom("tyger.discipline.sectypes.evidence",
                              [ast.alias("*")], 0)

    def types_import_to_ast(self):
        type_imports = [
            ast.ImportFrom("typing", [ast.alias("Callable")], 0),
            ast.ImportFrom("tyger.discipline.sectypes.types", [ast.alias("*")], 0),
        ]
        return type_imports

    def runtime_import_to_ast(self) -> list[ast.ImportFrom]:
        return [
            *super().runtime_import_to_ast(),
            ast.ImportFrom("tyger.discipline.sectypes.evidence", [ast.alias("custom_call")], 0)
        ]
