# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import ast
from typing import Callable, get_args, Any

from tyger.discipline.ToAST import ASTElaborator
from tyger.discipline.base.types import unk
from tyger.discipline.types import TypeException
from tyger.phase import Phase
from tyger.runtime.wrapper import ErrorLocation

renamings: dict[str, str] = {
    'range': 'Range'
}
Environment = dict[str, type]


def get_target_type(t: ast.expr) -> tuple | type:
    match t:
        case ast.Name() | ast.Subscript():
            return t.__target_type__
        case ast.List(elts) | ast.Tuple(elts):
            return tuple(get_target_type(el) for el in elts)
        case _:
            raise Exception("Unsupported target type")


class ElaborationPhase(Phase):

    def __init__(self, elaborator: ASTElaborator):
        self.to_ast = elaborator
        self.dependencies: dict[str, ast.Module] = {}
        self.elab_modules: set[str] = set()

    def elaborate_expr(self, node: ast.expr) -> ast.expr:
        context = node.__context__ if hasattr(node, "__context__") else None
        match node:
            case ast.Name(idx, ctx):
                if idx in renamings.keys():
                    idx = renamings[idx]
                elab_node = ast.Name(idx, ctx)
            case ast.Constant(value):
                elab_node = node
            case ast.Tuple(elts, ctx):
                elab_elts = [self.elaborate_expr(el) for el in elts]
                elab_node = ast.Tuple(elab_elts, ctx)
            case ast.Lambda(args, body):
                iterp = self.elaborate_expr(body)
                elab_node = ast.Lambda(args, iterp)
            case ast.Call(func, args, keywords):
                ty = func.__type__
                dom, cod = func.__signature__
                func = self.elaborate_expr(func)
                if len(args) > len(dom):
                    dom = dom + [unk for _ in range(len(args) - len(dom))] # TODO: check this
                argsp = []
                for expected_type, arg in zip(dom, args):
                    argp = self.to_ast.cast_elaborated(arg, expected_type)
                    argsp.append(argp)
                if ty.__qualname__ == unk.__qualname__:
                    func = self.to_ast.cast_elaborated(func, Callable[[*dom], cod]) # TODO: and this
                elab_node = self.to_ast.call_to_ast(func, argsp, keywords, context, ty)

            case ast.BinOp(left, op, right):
                dom = op.__signature__[0]
                lb = self.elaborate_expr(left)
                rb = self.elaborate_expr(right)
                lb = self.to_ast.cast_elaborated(lb, dom[0])
                rb = self.to_ast.cast_elaborated(rb, dom[1])
                # if not lty == dom[0]:
                #     ev = interior(lty, dom[0])
                #     lb = cast_to_ast(lb, ev)
                # if not rty == dom[1]:
                #     ev = interior(rty, dom[1])
                #     rb = cast_to_ast(rb, ev)
                elab_node = ast.BinOp(lb, op, rb)

            case ast.Compare(left, ops, comparators):
                # TODO: multiple comparators and comp_ops
                right = comparators[0]
                op = ops[0]
                lty, rty = left.__type__, right.__type__
                lb = self.elaborate_expr(left)
                rb = self.elaborate_expr(right)
                dom = op.__signature__[0]
                lb = self.to_ast.cast_elaborated(lb, dom[0])
                rb = self.to_ast.cast_elaborated(rb, dom[1])
                elab_node = ast.Compare(lb, ops, [rb])

            case ast.UnaryOp(op, operand):
                # TODO[FIX]:
                # TODO: support more ops. Currently only N
                vty = node.__type__
                iterp = self.elaborate_expr(operand)
                dom = op.__signature__[0]
                if type(op) is type(ast.Not()):
                    elab_node = self.to_ast.not_to_ast(iterp)
                else:
                    if not vty == dom[0]:
                        iterp = self.to_ast.cast_elaborated(iterp, dom[0])
                    elab_node = ast.UnaryOp(op, iterp)
            case ast.List(elts, ctx):
                # print("expected", expected)
                # we decide to wrap the list based on the expected type if there is any.
                ty = node.__type__  # Assume type list
                elem_ty = get_args(ty)[0]
                # now we wrap each element if necessary
                elts_p = []
                for e in elts:
                    vty = e.__type__
                    iterp = self.elaborate_expr(e)
                    if vty != elem_ty:
                        iterp = self.to_ast.cast_elaborated(iterp, elem_ty)
                    elts_p.append(iterp)
                elab_node = ast.List(elts_p, ctx)

            case ast.Subscript(value, slice, ctx):
                iterp = self.elaborate_expr(value)
                # if vty.__qualname__ != list.__qualname__ and vty.__qualname__ != tuple.__qualname__:
                #    raise TypeException(f"Type mismatch: {vty} != list")

                sb = self.elaborate_expr(slice)
                # sb = self.to_ast.cast_elaborated(sb, value.__dom__)
                # # if not a slice, then it must be an integer
                # if sty.__qualname__ != tslice.__qualname__ and sty != int:
                #     sb = self.to_ast.cast_elaborated(sb, int)
                sb = self.to_ast.unwrap_value_to_ast(sb)
                elab_node = ast.Subscript(iterp, sb, ctx)
            case ast.Slice(lower, upper, step):
                lowerp = None
                upperp = None
                stepp = None
                if lower:
                    lb = self.elaborate_expr(lower)
                    lb = self.to_ast.cast_elaborated(lb, int)
                    lowerp = self.to_ast.unwrap_value_to_ast(lb)
                if upper:
                    ub = self.elaborate_expr(upper)
                    ub = self.to_ast.cast_elaborated(ub, int)
                    upperp = self.to_ast.unwrap_value_to_ast(ub)
                if step:
                    sb = self.elaborate_expr(step)
                    sb = self.to_ast.cast_elaborated(sb, int)
                    stepp = self.to_ast.unwrap_value_to_ast(sb)
                elab_node = ast.Slice(lowerp, upperp, stepp)
            case ast.ListComp(elt, generators):
                # TODO: support more generators than just lists.
                generatorsp = []
                ifsp = []
                for g in generators:
                    match g:
                        case ast.comprehension(target, iter, ifs, is_async):
                            ty = iter.__type__
                            iterp = self.elaborate_expr(iter)
                            # print("what",ty, iter)
                            # print("typing ", ast.unparse(iter), ty, env)
                            inner_ty = unk
                            if ty.__qualname__ == unk.__qualname__:
                                iterp = self.to_ast.cast_elaborated(iter, list[unk])
                            else:
                                inner_ty = get_args(ty)[0]
                            iterp = self.to_ast.unwrap_value_to_ast(iterp)

                            if len(ifs) > 0:
                                # first we transform multiple ifs in a single if
                                ifp = ast.BoolOp(ast.And(), ifs) if len(ifs) > 1 else ifs[0]
                                ifp.__type__ = bool  # TODO: maybe don't hardcode this
                                ifp.__context__ = ifs[0].__context__
                                # then we transform it
                                ifp = self.elaborate_expr(ifp)
                                # and wrap the condition so it may propagate evidences
                                ifsp = [self.to_ast.list_comp_if_to_ast(ifp)]

                            generatorsp.append(ast.comprehension(target, iterp, ifsp, is_async))
                        case _:
                            raise Exception(f"Unsupported generator: {g}")
                vty = elt.__type__
                eltp = self.elaborate_expr(elt)
                eltp = self.to_ast.cast_elaborated(eltp, vty)
                elab_node = self.to_ast.list_comp_to_ast(eltp, generatorsp, ifsp)  # ListComp(eltp, generatosp)
            case ast.BoolOp(op, values):
                valuesp = [self.to_ast.cast_elaborated(v, node.__type__) for v in values]
                elab_node = self.to_ast.bool_op_to_ast(op, valuesp)
            case ast.Attribute(value, attr, ctx):
                elab_node = node
            case ast.IfExp(test, body, orelse):
                testp = self.elaborate_expr(test)
                bodyp = self.elaborate_expr(body)
                orelsep = self.elaborate_expr(orelse)
                # Cast subexpressions
                error_loc = ErrorLocation(node.lineno, node.col_offset)
                testp = self.to_ast.cast_elaborated(testp, test.__type__, error_loc)
                bodyp = self.to_ast.cast_elaborated(bodyp, body.__type__, error_loc)
                orelsep = self.to_ast.cast_elaborated(orelsep, orelse.__type__, error_loc)
                elab_node = self.to_ast.ifexp_to_ast(testp, bodyp, orelsep)

            case ast.Dict(keys, values):
                # We will first type each of the keys, computing the join of resulting types
                key_locs = [ErrorLocation(key.lineno, key.col_offset) for key in keys]
                value_locs = [ErrorLocation(val.lineno, val.col_offset) for val in values]

                dict_type = node.__type__
                keys_type, values_type = get_args(dict_type)

                keysp = [self.elaborate_expr(key) for key in keys]
                valuesp = [self.elaborate_expr(value) for value in values]

                casted_keys = [self.to_ast.cast_elaborated(key, keys_type, error) for key, error in zip(keysp, key_locs)]
                casted_values = [self.to_ast.cast_elaborated(value, values_type, error) for value, error in
                                 zip(valuesp, value_locs)]

                elab_node = ast.Dict(casted_keys, casted_values)
            case _:
                raise Exception(f"Unsupported expression: {node}")
        elab_node.__type__ = node.__type__
        elab_node.__context__ = node.__context__
        return elab_node

    def elaborate_stmt(self, node: ast.stmt) -> list[ast.stmt]:
        context = getattr(node, "__context__", None)
        match node:
            case ast.Expr(value):
                return [ast.Expr(self.elaborate_expr(value))]
            case ast.FunctionDef(names, args, body, returns=returns):
                node.body = self.elaborate_block(node.body)
                return [node]
            case ast.Assign(targets, value):

                # Assignment is a complex monster. Targets represent expressions preceding the value which is assigned
                # We simplify assignments with multiple targets to multiple assignments with single target

                # We prepare target processing, by first type_checking the value
                vty = value.__type__
                valuep = self.elaborate_expr(value)

                assign_list = []
                # We store the obtained value in a variable, with some obscure names, IF WE HAVE MULTIPLE TARGETS
                if len(targets) > 1:
                    variable_name = f"__{node.lineno}_var"
                    var_assign = ast.Assign([ast.Name(variable_name, ast.Store())], valuep)
                    assign_list = [var_assign]
                    valuep = ast.Name(variable_name, ast.Load())
                    valuep.__type__ = vty
                    valuep.__context__ = value.__context__
                for t in targets:
                    target_type: tuple | type = get_target_type(t)
                    prev_val, transformed_target = self.elaborate_target(t)

                    match target_type:
                        case tuple():
                            # Casting
                            casted_value = self.to_ast.cast_each(valuep, target_type, vty)
                            new_assign = self.to_ast.assign_to_ast([transformed_target], None, casted_value, context)
                            assign_list.extend(new_assign)
                        case _:  # just a type

                            # Cast value according to typ
                            casted_value = self.to_ast.cast_elaborated(valuep, target_type)  # TODO: error_location

                            # Create new assignment node
                            new_assign = self.to_ast.assign_to_ast([transformed_target], target_type, casted_value, context,
                                                                   prev_val)

                            # Append new assignment node to list
                            assign_list.extend(new_assign)

                return assign_list

            case ast.AnnAssign(target, annotation, value, simple):
                # return linear, [node]
                match target:
                    case ast.Name(idx):
                        # print("an assign ", id)
                        typ = target.__target_type__
                        prev_val = target.__prev_val__
                        # print("prev value for ", id, prev_val)
                        # we pass the annotated type to the expression in case we need to use it to infer the type of an iterable.
                        # print(ast.dump(node))

                        if value:
                            valuep = self.elaborate_expr(value)
                            valuep = self.to_ast.cast_elaborated(valuep, typ)
                        else:
                            valuep = value
                        return self.to_ast.ann_assign_to_ast(target, annotation, typ, valuep, simple, context, prev_val)

            case ast.Return(value):
                ty = value.__type__
                valuep = self.elaborate_expr(value)
                # ev_expected = None
                exp = context.expected
                typ = context.taint_type(node, ty)

                # TODO: why double cast?
                valuep = self.to_ast.cast_elaborated(valuep, typ, ErrorLocation(node.lineno, node.col_offset))
                valuep.__type__ = typ
                valuep = self.to_ast.cast_elaborated(valuep, exp, ErrorLocation(node.lineno, node.col_offset))
                # if exp and not consistent(typ, exp):
                #     raise TypeException(f"Type mismatch: {typ} != {exp}")
                # elif exp and typ != exp:
                #     ev = interior(typ, exp)
                #     b = cast_to_ast(b, ev, ErrorLocation(node.lineno, node.col_offset))
                # else:
                #     ev_expected = interior(exp, exp)

                return self.to_ast.return_to_ast(
                    valuep)  # , ev_expected) #the ev_expected was a test to see if we could avoid the cast
            case ast.If(test, body, or_else):
                testp = self.elaborate_expr(test)
                # we make a copy of the linear environment as branches should not modify typing information of variables
                # in scope. This is not true!! FIXED
                bodyp = self.elaborate_block(body)
                orelsep = self.elaborate_block(or_else)
                return self.to_ast.ite_to_ast(testp, bodyp, orelsep)

            case ast.While(test, body, or_else):
                testp = self.elaborate_expr(test)
                bodyp = self.elaborate_block(body)
                orelsep = self.elaborate_block(or_else)
                return self.to_ast.while_to_ast(testp, bodyp, orelsep)
            case ast.For(target, iterx, body, or_else):
                iterp = self.elaborate_expr(iterx)
                # TODO: refactor in an extract function
                if iterx.__type__.__qualname__ == unk.__qualname__:
                    iterp = self.to_ast.cast_elaborated(iterp, list[unk])
                bodyp = self.elaborate_block(body)
                orelsep = self.elaborate_block(or_else)
                return self.to_ast.for_to_ast(target, iterp, bodyp, orelsep)
            case ast.AugAssign(target, op, value):
                load_target = ast.Name(target.id, ast.Load())
                load_target.__type__ = target.__target_type__
                load_target.__context__ = value.__context__
                binop = ast.BinOp(load_target, op, value)
                _, cod = op.__signature__
                binop.__type__ = cod
                binop.__context__ = context  # TODO: what context should I propagate?
                nodep = ast.Assign([target], binop)
                nodep.__context__ = context
                nodep.lineno = node.lineno
                nodep.col_offset = node.col_offset
                return self.elaborate_stmt(nodep)
            case ast.Pass():
                return [ast.Pass()]
            case ast.ClassDef(names, bases, keywords, body, decorator_list):
                if len(bases) > 0:
                    raise TypeException(f"Unsupported operation: {node} for nont-empty bases") # TODO: IMPLEMENT CLASSES!
                else:
                    node.body = [self.elaborate_stmt(st) for st in body]
                    return [node]
            case ast.Import(names):
                for name in names:
                    if name.name.startswith("tyger") or name.name.startswith("typing"):
                        return [node]
                    module_name = name.name
                    if module_name not in self.elab_modules:
                        module_ast = self.dependencies[module_name]
                        elab_module = self.elaborate_top_level(module_ast)
                        self.elab_modules.add(module_name)
                        elab_src = ast.unparse(ast.fix_missing_locations(elab_module))
                        init_stmt = self.to_ast.init_module_to_ast(module_name, elab_src)
                        return init_stmt + self.to_ast.import_to_ast(node)
                    else:
                        return self.to_ast.import_to_ast(node)
            case ast.ImportFrom(module, names, level):
                if module.startswith("tyger") or module.startswith("typing"):
                    return [node]
                module_name = node.__full_name__
                init_stmts = []
                if module_name not in self.elab_modules:
                    module_ast = self.dependencies[module_name]
                    elab_module = self.elaborate_top_level(module_ast)
                    self.elab_modules.add(module_name)
                    elab_src = ast.unparse(ast.fix_missing_locations(elab_module))
                    init_stmts.extend(self.to_ast.init_module_to_ast(module_name, elab_src))
                # Now maybe one of the imported names is also a module, so we should try to initialize it
                for name in names:
                    submodule_name = name.name
                    full_submodule_name = f"{module_name}.{submodule_name}"
                    if full_submodule_name in self.dependencies and full_submodule_name not in self.elab_modules:
                        init_stmts.extend(self.elab_init_module(full_submodule_name))
                return init_stmts + self.to_ast.import_from_to_ast(node)
            case _:
                raise Exception(f"Unsupported statement: {node}")

    def elab_init_module(self, module_name):
        module_ast = self.dependencies[module_name]
        elab_module = self.elaborate_top_level(module_ast)
        self.elab_modules.add(module_name)
        elab_src = ast.unparse(ast.fix_missing_locations(elab_module))
        init_stmt = self.to_ast.init_module_to_ast(module_name, elab_src)
        return init_stmt

    def elaborate_target(self, node: ast.expr) -> tuple[ast.expr, ast.expr]:

        """
        Gets the expected type of a node which acts as an assignment target.
        For subscription, it also typechecks the slice.
        Returns the expected type of the target. If the target is a tuple or a list, returns each inner target type.
        """

        # We will only support assignment to Name's attributes and subscripts.
        # We will figure out other cases later
        prev_val = ast.Constant(None)
        new_target = node  # Must be set on each case!
        match node:
            case ast.Name(idx):
                target_type = node.__target_type__
                if target_type:
                    prev_val = ast.Name(idx, ast.Load())
            case ast.Attribute(value, attr):
                prev_val = ast.Attribute(value, attr, ast.Load())
            case ast.Subscript(value, sl):
                match value:
                    case ast.Name(value_id):
                        target_type = node.__target_type__
                        if target_type:
                            value_type = value.__type__
                            slice_typ = sl.__type__
                            tr_slice = self.elaborate_expr(sl)
                            match value_type.__qualname__:
                                # TODO: how to elaborate lists indexes?
                                case dict.__qualname__:
                                    dom, cod = get_args(value_type)
                                    tr_slice = self.to_ast.cast_elaborated(tr_slice, dom)
                                    prev_val = ast.Subscript(value, sl, ast.Load())
                                    new_target.slice = tr_slice
                    case _:
                        raise Exception("Unsupported subscript target")

            case ast.List(elts):
                prev_vals = []
                eltsp = []
                for el in elts:
                    prev_val, elp = self.elaborate_target(el)
                    prev_vals.append(prev_val)
                    eltsp.append(elp)
                prev_val = ast.List(prev_vals, ast.Load())
                new_target = ast.List([*eltsp], ast.Store())
            case ast.Tuple(elts):
                prev_vals = []
                eltsp = []
                for el in elts:
                    prev_val, elp = self.elaborate_target(el)
                    prev_vals.append(prev_val)
                    eltsp.append(elp)
                prev_val = ast.Tuple(prev_vals, ast.Load())
                new_target = ast.Tuple([*eltsp], ast.Store())
            case ast.Starred(value):
                raise Exception("Unsupported expression Starred")
        return prev_val, new_target

    def elaborate_block(self, block: list[ast.stmt]) -> list[ast.stmt]:
        new_block = []
        for st in block:
            new_block.extend(self.elaborate_stmt(st))
        return new_block

    def elaborate_top_level(self, source: ast.Module) -> ast.Module:
        # We need to import Wrappers and Evidence
        wrapper_import: list[ast.ImportFrom] = self.to_ast.runtime_import_to_ast()
        types_import: list[ast.ImportFrom] = self.to_ast.types_import_to_ast()
        evidence_import = self.to_ast.evidence_import_to_ast()
        source.body = [*wrapper_import, *types_import, evidence_import] + self.elaborate_block(source.body)
        return source

    def run(self, source: ast.Module, **kwargs) -> tuple[ast.Module, dict[str, Any]]:
        # We first elaborate the dependencies
        deps = kwargs.get("dependencies", {})
        self.dependencies = deps
        source = self.elaborate_top_level(source)
        return source, kwargs







