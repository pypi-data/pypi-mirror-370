import ast
import builtins
import functools
from typing import Any, Callable, get_args

from tyger.diagnostics.diagnostics import TygerDiagnostic
from tyger.diagnostics.warnings import (
    RedefineVariableWarning,
    UndefinedVariableWarning,
    UnsupportedExprWarning,
    UnsupportedTypeWarning,
)
from tyger.discipline.base.types import TypeName, unk  # TODO: remove this dependency
from tyger.discipline.types import Context, TypeSystem
from tyger.diagnostics.errors import (
    AttributeNotFoundError,
    CriticalTypeCheckError,
    NotFoundBinOpTypeError,
    NotFoundUnOpTypeError,
    NotFoundTypeError,
    TypeMismatchError,
)
from tyger.diagnostics.errors import ArityMismatchError
from tyger.phase import Phase
from tyger.phases.dependency_collection import resolve_full_name

default_types: dict[str, type] = {
    "range": Callable[[int, int, int], list[int]],
    "print": Callable[[unk], unk],
}

renamings: dict[str, str] = {"range": "Range"}

callable_builtins = ["print"]

Environment = dict[str, type]


class Spec:
    def __init__(self, spec: dict[str, type]):
        self.spec = spec


class SpecEnv:
    classes = {}

    def addSpec(self, name: str, spec: Spec):
        self.classes[name] = spec


class TypingPhase(Phase):
    def __init__(self, type_system: TypeSystem, file_path: str = None):
        self.type_system = type_system
        self.namespaces = None
        self.deps = None
        self.diagnostics: list[TygerDiagnostic] | None = None
        self.current_file_path = file_path
        self.file_paths = {}

    def collect_specs(self, nodes: list[ast.stmt]) -> SpecEnv:
        spec_env = SpecEnv()
        for node in nodes:
            match node:
                # TODO: do something with the bases
                case ast.ClassDef(name, bases, keywords, body, decorator_list):
                    spec = {}
                    for b in body:
                        match b:
                            case ast.FunctionDef(
                                name, args, body, returns
                            ) if name.startswith("__"):
                                ty, _ = self.function_signature(b, {}, None)
                                spec[name] = ty
                                # TODO: stuck! we have to typecheck the body of the function
                    spec_env.addSpec(name, Spec(spec))

    def collect_assigned_vars(self, nodes: list[ast.stmt]) -> list[str]:
        vars = []
        for node in nodes:
            match node:
                case ast.Assign(targets, value):
                    for target in targets:
                        match target:
                            case ast.Name(id):
                                vars.append(id)
                            # case _: TODO: support for tuples and objects
                            case _:
                                self.diagnostics.append(
                                    UnsupportedExprWarning(
                                        node,
                                        f"Unsupported target",
                                        self.current_file_path,
                                    )
                                )
                case ast.AnnAssign(target, annotation, value, simple):
                    match target:
                        case ast.Name(id):
                            vars.append(id)
                        case _:
                            self.diagnostics.append(
                                UnsupportedExprWarning(
                                    node,
                                    f"Unsupported target: {target}",
                                    self.current_file_path,
                                )
                            )
        return vars

    def type_check_expr_to_type(
        self, node: ast.expr, env: Environment, target_type: type, context
    ) -> type:
        typ = self.type_check_expr(node, env, context)
        if not self.type_system.consistent(typ, target_type):
            self.diagnostics.append(
                TypeMismatchError(node, typ, target_type, self.current_file_path)
            )
        return typ

    def get_expected_type(
        self, node: ast.expr, env: Environment, context: Context
    ) -> tuple | type | None:
        """
        Gets the expected type of a node which acts as an assignment target.
        For subscription, it also typechecks the slice.
        Returns the expected type of the target. If the target is a tuple or a list, returns each inner target type.
        """

        # We will only support assignment to Name's attributes and subscripts.
        # We will figure out other cases later
        exp_type = None
        match node:
            case ast.Name(idx):
                if idx in env:
                    exp_type = env[idx]
                # We annotate in direct targets only (*)
                node.__target_type__ = exp_type
            case ast.Subscript(value, slice):
                match value:
                    case ast.Name(value_id):
                        if value_id in env:
                            value_type = env[value_id]
                            value.__type__ = value_type
                            slice_typ = self.type_check_expr(slice, env, context)
                            match value_type.__qualname__:
                                case list.__qualname__:
                                    # Typecheck index. Lists may be indexed by integers or slices
                                    self.type_system.check_slice_type(
                                        value_type, slice_typ
                                    )
                                case dict.__qualname__:
                                    dom, cod = get_args(value_type)
                                    try:
                                        self.check_consistency(dom, slice_typ, node)
                                    except TypeMismatchError as tme:
                                        self.diagnostics.append(
                                            TypeMismatchError(
                                                node,
                                                tme.actual_type,
                                                tme.expected_type,
                                                self.current_file_path,
                                            )
                                        )
                                    exp_type = cod
                        node.__target_type__ = exp_type
                    case _:
                        self.diagnostics.append(
                            UnsupportedExprWarning(
                                node,
                                f"Unsupported subscript target: {value}",
                                self.current_file_path,
                            )
                        )

            case ast.List(elts) | ast.Tuple(elts):
                exp_type = tuple(
                    self.get_expected_type(el, env, context) for el in elts
                )
            case ast.Starred(value):
                self.diagnostics.append(
                    UnsupportedExprWarning(
                        node,
                        f"Unsupported starred expression: {value}",
                        self.current_file_path,
                    )
                )
        return exp_type

    def type_check_expr(
        self,
        node: ast.expr,
        env: Environment = None,
        context: Context = Context.initial(),
    ) -> type | dict[str, Any]:
        env = env or {}
        node.__tags__ = {}
        match node:
            case ast.Name(idx):
                envs = {**default_types, **env}
                t = envs[idx] if idx in envs.keys() else None
                if not t:
                    if not hasattr(builtins, idx):
                        self.diagnostics.append(
                            UndefinedVariableWarning(
                                node, f"{idx} is not defined", self.current_file_path
                            )
                        )
                    t = self.type_system.get_default_type()

            case ast.Constant(value):
                t = self.type_system.type_of(value)

            case ast.Tuple(elts, ctx):
                tys = [self.type_check_expr(elt, env, context) for elt in elts]
                t = tuple[*tys]

            case ast.Lambda(args, body):
                # we use unknown type, unless we are expecting a function type
                if context and context.expected:
                    dom, cod = self.type_system.extract_func_type(context.expected)
                    if len(args.args) < len(dom):
                        self.diagnostics.append(
                            ArityMismatchError(
                                node, len(dom), len(args.args), self.current_file_path
                            )
                        )
                else:
                    dom, cod = self.type_system.get_default_dom_cod(len(args.args))
                if len(dom) < len(args.args):
                    default_type = self.type_system.get_default_type()
                    dom.extend([default_type] * (len(args.args) - len(dom)))
                local: dict[str, type] = {x.arg: ty for x, ty in zip(args.args, dom)}
                self.type_check_expr_to_type(
                    body, {**env, **local}, cod, context.taint_context(node, cod)
                )
                # ty = self.type_check_expr(body, {**env, **local}, context.taint_context(node, cod))
                t = Callable[[*dom], cod]

            case ast.Call(func, args, keywords):
                ty = self.type_check_expr(func, env, context.no_expected())
                dom, cod = self.type_system.dom_cod(ty)
                if len(args) > len(dom):
                    default_type = self.type_system.get_default_type()
                    dom = dom + [default_type for _ in range(len(args) - len(dom))]
                for pair in zip(dom, args):
                    domty, arg = pair
                    self.type_check_expr_to_type(arg, env, domty, context.no_expected())
                func.__signature__ = (dom, cod)
                t = cod

            case ast.BinOp(left, op, right):
                lty = self.type_check_expr(left, env, context.no_expected())
                rty = self.type_check_expr(right, env, context.no_expected())
                try:
                    ty = self.type_system.type_of_bin_primitive(op, lty, rty)
                except NotFoundBinOpTypeError:
                    self.diagnostics.append(
                        NotFoundBinOpTypeError(
                            node, str(lty), str(rty), str(op), self.current_file_path
                        )
                    )
                    # TODO error: I have to check the use of unknown in these cases
                    ty = self.type_system.get_default_type()
                dom, cod = self.type_system.dom_cod(ty)
                op.__signature__ = (dom, cod)
                t = cod

            case ast.Compare(left, ops, comparators):
                lty = self.type_check_expr(left, env, context.no_expected())
                rty = self.type_check_expr(comparators[0], env, context.no_expected())
                try:
                    ty = self.type_system.type_of_bin_primitive(ops[0], lty, rty)
                except NotFoundBinOpTypeError:
                    self.diagnostics.append(
                        NotFoundBinOpTypeError(
                            node,
                            str(lty),
                            str(rty),
                            str(ops[0]),
                            self.current_file_path,
                        )
                    )
                    ty = self.type_system.get_default_type()
                dom, cod = self.type_system.dom_cod(ty)
                ops[0].__signature__ = (dom, cod)
                t = cod

            case ast.UnaryOp(op, operand):
                vty = self.type_check_expr(operand, env, context.no_expected())
                try:
                    ty = self.type_system.type_of_un_primitive(op, vty)
                except NotFoundUnOpTypeError:
                    self.diagnostics.append(
                        NotFoundUnOpTypeError(
                            node, str(vty), str(op), self.current_file_path
                        )
                    )
                    ty = self.type_system.get_default_type()
                dom, cod = self.type_system.dom_cod(ty)
                op.__signature__ = self.type_system.dom_cod(ty)
                t = cod

            case ast.List(elts, ctx):
                # TODO: Handle empty lists. We get "reduce() of empty iterable with no initial value"
                inner_ty = functools.reduce(
                    self.type_system.gjoin,
                    (
                        self.type_check_expr(elt, env, context.no_expected())
                        for elt in elts
                    ),
                )
                t = list[inner_ty]
            case ast.Subscript(value, sl, ctx):
                # c = a[1]
                # TODO: generalise subscription
                vty = self.type_check_expr(value, env, context.no_expected())
                if vty.__qualname__ == "GenericAlias":  # list[unk], dict[int,str]
                    return vty
                # Slice handling
                dom = self.type_system.get_domain(vty)
                value.__dom__ = dom
                sty = self.type_check_expr(sl, env, context.no_expected())
                try:
                    self.type_system.check_slice_type(vty, sty)
                except TypeError:
                    self.diagnostics.append(
                        TypeMismatchError(
                            node,
                            str(vty),
                            str(sty),
                            self.current_file_path,
                        )
                    )
                # here we are assuming that the value is a list or a tuple
                t = self.type_system.get_inner_type(vty)
                # args = get_args(vty)
                # t = args[0] if vty.__qualname__ == list.__qualname__ else unk

            case ast.Slice(lower, upper, step):
                if lower:
                    self.type_check_expr(lower, env, context.no_expected())
                if upper:
                    self.type_check_expr(upper, env, context.no_expected())
                if step:
                    self.type_check_expr(step, env, context.no_expected())
                t = self.type_system.get_slice_type()
            case ast.ListComp(elt, generators):
                menv = {}
                for g in generators:
                    match g:
                        case ast.comprehension(target, _iter, ifs, is_async):
                            ty = self.type_check_expr(_iter, env, context.no_expected())
                            inner_ty = self.type_system.get_inner_type(ty)
                            menv[target.id] = inner_ty
                            for i in ifs:
                                self.type_check_expr(
                                    i, {**env, **menv}, context.no_expected()
                                )
                        case _:
                            self.diagnostics.append(
                                UnsupportedExprWarning(
                                    node,
                                    f"Unsupported generator: {g}",
                                    self.current_file_path,
                                )
                            )
                vty = self.type_check_expr(elt, {**env, **menv}, context.no_expected())
                t = list[vty]

            case ast.BoolOp(op, values):
                ts = [self.type_check_expr(value, env, context) for value in values]
                t = functools.reduce(self.type_system.gjoin, ts)

            case ast.Attribute(value, attr, ctx):
                # a = b.c
                vty = self.type_check_expr(value, env, context.no_expected())
                try:
                    ty = vty[attr]
                except (TypeError, KeyError):  # Unk is not subscriptable
                    self.diagnostics.append(
                        AttributeNotFoundError(node, attr, self.current_file_path)
                    )
                    ty = self.type_system.get_default_type()
                t = ty

            case ast.IfExp(test, body, orelse):
                self.type_check_expr(test, env, context.no_expected())
                body_type = self.type_check_expr(body, env, context)
                orelse_type = self.type_check_expr(orelse, env, context)
                t = self.type_system.gjoin(body_type, orelse_type)

            case ast.Dict(keys, values):
                key_type = functools.reduce(
                    self.type_system.gjoin,
                    (self.type_check_expr(key, env, context) for key in keys),
                )
                value_type = functools.reduce(
                    self.type_system.gjoin,
                    (self.type_check_expr(val, env, context) for val in values),
                )
                t = dict[key_type, value_type]

            case ast.JoinedStr(values):
                # F-string support
                for value in values:
                    match value:
                        case ast.FormattedValue(
                            value=expr, conversion=_, format_spec=format_spec
                        ):
                            self.type_check_expr(expr, env, context.no_expected())
                            if format_spec:
                                self.type_check_expr(
                                    format_spec, env, context.no_expected()
                                )
                        case ast.Constant(_):
                            pass
                        case _:
                            self.type_check_expr(value, env, context.no_expected())
                # F-strings always evaluate to str
                t = str

            case _:
                self.diagnostics.append(
                    UnsupportedExprWarning(
                        node,
                        f"Unsupported expression: {node}",
                        self.current_file_path,
                    )
                )

        node.__type__ = t
        node.__context__ = context
        return t

    def extend_environment(self, target: ast.expr, typ: type, env: Environment):
        match target:
            case ast.List(elts) | ast.Tuple(elts):
                # TODO: extract typing logic to type_system
                # Case like [x,y,z] = foo()
                typs = self.type_system.unwrap_value_type(typ, len(elts))
                for el, ty in zip(elts, typs):
                    env = self.extend_environment(el, ty, env)
            case ast.Name(idx):
                if not target.__target_type__:
                    target.__target_type__ = typ
                if idx not in env:
                    env[idx] = typ
            case ast.Subscript(value, sl):
                match value:
                    case ast.Name(idx):
                        if idx not in env:
                            self.diagnostics.append(
                                NotFoundTypeError(target, idx, self.current_file_path)
                            )
        return env

    def type_check_stmt(
        self,
        node: ast.stmt,
        linear: Environment = None,
        context: Context = None,
        package_name: str = "",
    ) -> Environment:
        linear = linear or self.type_system.get_builtin_types()
        context = context or self.type_system.get_initial_context()
        ret_env = linear
        match node:
            case ast.Expr(value):
                self.type_check_expr(value, linear, context)
            case ast.FunctionDef(name, args, body, returns=returns):
                dom = []
                for arg in args.args:
                    if arg.annotation:
                        ann_type = self.type_check_expr(arg.annotation, linear, context)
                        # self.type_system.check_annotation_type(ann_type)
                        match arg.annotation:
                            case ast.Attribute(value, attr):
                                # We obtain the type from the attribute itself. TODO: support attribute
                                dom.append(
                                    self.type_system.parse_type(
                                        ast.Name(attr, ast.Load())
                                    )
                                )
                            case _:
                                # Check for Union/Optional types in function arguments
                                if isinstance(arg.annotation, ast.Subscript):
                                    if isinstance(arg.annotation.value, ast.Name) and arg.annotation.value.id in ["Union", "Optional"]:
                                        self.diagnostics.append(
                                            UnsupportedTypeWarning(
                                                arg.annotation,
                                                f"Union and Optional types are not fully supported: {ast.unparse(arg.annotation)}",
                                                self.current_file_path
                                            )
                                        )
                                    elif isinstance(arg.annotation.value, ast.Attribute) and arg.annotation.value.attr in ["Union", "Optional"]:
                                        self.diagnostics.append(
                                            UnsupportedTypeWarning(
                                                arg.annotation,
                                                f"Union and Optional types are not fully supported: {ast.unparse(arg.annotation)}",
                                                self.current_file_path
                                            )
                                        )
                                dom.append(self.type_system.parse_type(arg.annotation))
                    else:
                        dom.append(unk)
                if returns:
                    ret_ann_type = self.type_check_expr(returns, linear, context)
                    # self.type_system.check_annotation_type(ret_ann_type)
                    match returns:
                        case ast.Attribute(value, attr):
                            cod = self.type_system.get_cod_type_from_annotation(
                                self.get_type_from_annotation(
                                    ast.Name(attr, ast.Load())
                                )
                            )
                        case _:
                            cod = self.type_system.get_cod_type_from_annotation(
                                self.get_type_from_annotation(returns)
                            )

                else:
                    cod = unk
                t = Callable[[*dom], cod]
                node.__type__ = t
                linear[name] = t
                # ty, variables = self.function_signature(node, linear, context)
                # xs = collect_assigned_vars(body, self.current_file_path)
                # dom, cod = get_args(ty)
                # newlinear = {**{k: v for k, v in linear.items() if k not in xs}, name: ty, **variables}
                # self.type_check_stmts(body, newlinear, context.taint_context(node, cod))
            case ast.Assign(targets, value):

                # Assignment is a complex monster. Targets represent expressions preceding the value which is assigned
                # We simplify assignments with multiple targets to multiple assignments with single target

                # We prepare target processing, by first type_checking the value
                vty = self.type_check_expr(value, linear, context)
                for t in targets:
                    target_type = self.get_expected_type(t, linear, context)
                    try:
                        self.check_consistency(target_type, vty, node)
                    except TypeMismatchError as tme:
                        self.diagnostics.append(
                            TypeMismatchError(
                                node,
                                tme.actual_type,
                                tme.expected_type,
                                self.current_file_path,
                            )
                        )
                    linear = self.extend_environment(t, vty, linear)

            case ast.AnnAssign(target, annotation, value, simple):
                match target:
                    case ast.Name(idx):
                        if idx in linear:
                            self.diagnostics.append(
                                RedefineVariableWarning(
                                    node, idx, self.current_file_path
                                )
                            )

                        ann_ty = self.type_check_expr(annotation, linear, context)
                        if self.type_system.check_annotation_type(ann_ty):
                            ty = self.type_system.parse_type(annotation)
                        else:
                            ty = self.type_system.get_default_type()
                        typ = context.taint_type(node, ty)
                        target.__target_type__ = typ
                        target.__prev_val__ = (
                            ast.Name(idx, ast.Load())
                            if idx in linear
                            else ast.Constant(None)
                        )
                        if value:
                            self.type_check_expr_to_type(
                                value, linear, typ, context.taint_context(node, typ)
                            )
                        # TODO: check this redef
                        linear[idx] = typ

            case ast.Return(value):
                vty = self.type_check_expr(value, linear, context)
                try:
                    self.check_consistency(context.expected, vty, node)
                    self.check_consistency(
                        context.expected, context.taint_type(node, vty), node
                    )
                except TypeMismatchError as tme:
                    self.diagnostics.append(
                        TypeMismatchError(
                            node,
                            tme.actual_type,
                            tme.expected_type,
                            self.current_file_path,
                        )
                    )

            case ast.If(test, body, or_else) | ast.While(test, body, or_else):
                ty = self.type_check_expr(test, linear, context)
                contextp = context.taint_context(node, ty)
                l = self.type_check_stmts(body, linear, contextp)
                l = self.type_check_stmts(or_else, l, contextp)
                ret_env = l

            case ast.For(target, iter, body, or_else):
                ty = self.type_check_expr(iter, linear, context)
                inner_ty = self.type_system.get_inner_type(ty)
                linear[target.id] = inner_ty
                contextp = context.taint_context(
                    context.taint_context(node, ty), inner_ty
                )  # should it be tainted by ty or inner_ty?, better to taint both
                l = self.type_check_stmts(body, linear, contextp)
                l = self.type_check_stmts(or_else, l, contextp)
                ret_env = l
            case ast.AugAssign(target, op, value):
                # TODO: type_check op
                target_type = self.get_expected_type(target, linear, context)
                value_type = self.type_check_expr(value, linear, context)
                try:
                    op_type = self.type_system.type_of_bin_primitive(
                        op, target_type, value_type
                    )
                except NotFoundBinOpTypeError:
                    self.diagnostics.append(
                        NotFoundBinOpTypeError(
                            node,
                            str(target_type),
                            str(value_type),
                            str(op),
                            self.current_file_path,
                        )
                    )
                    op_type = self.type_system.get_default_type()
                op.__signature__ = self.type_system.dom_cod(op_type)
                return linear
            case ast.Pass():
                pass
            case ast.ClassDef(name, bases, keywords, body, decorator_list):
                if len(bases) > 0:
                    self.diagnostics.append(
                        UnsupportedExprWarning(
                            node,
                            f"Unsupported operation: {node} for non-empty bases",
                            self.current_file_path,
                        )
                    )
                else:
                    linear = self.type_check_stmts(body, linear, context)
                    return linear
            case ast.ImportFrom(module, name, level):
                module_name = resolve_full_name(module, level, package_name)
                _ = self.update_namespaces(module_name)
                module_env = self.get_module_env(module_name)
                for name in name:
                    if name.name == "*":
                        linear.update(module_env)
                        break
                    as_name = name.asname or name.name
                    if name.name in module_env:
                        linear[as_name] = module_env[name.name]
                    else:
                        try:
                            submodule_name = f"{module_name}.{name.name}"
                            _ = self.update_namespaces(submodule_name)
                            submodule_env = self.get_module_env(submodule_name)
                            linear[as_name] = submodule_env
                        except ModuleNotFoundError:
                            self.diagnostics.append(
                                AttributeNotFoundError(
                                    node, name.name, module_name, self.current_file_path
                                )
                            )
            case ast.Import(name):
                for name in name:
                    # Update namespaces
                    module_name: str = name.name
                    if module_name.startswith(
                        "tyger.discipline"
                    ) and module_name.endswith("types"):
                        # We are importing a tyger type system. We should check that it matches the given discipline
                        imported_discipline = module_name
                        running_discipline = self.type_system.__module__
                        if imported_discipline == running_discipline:

                            linear[name.asname or module_name] = (
                                self.type_system.get_types()
                            )
                            continue  # We don't typecheck tyger!
                        else:
                            raise CriticalTypeCheckError(
                                node,
                                f"Discipline mismatch: {imported_discipline} != {running_discipline}",
                                self.current_file_path,
                            )
                    top_module_name = self.update_namespaces(module_name)
                    if name.asname:
                        # If the name is imported with an alias, we should bind the submodule namespace to that alias
                        module_env = self.get_module_env(module_name)
                        module_alias = name.asname
                    else:
                        # If the name is not imported with an alias, we should bind the top module namespace to the top name
                        # For example, when importing module.submodule, we should bind module's namespace to 'module'
                        module_env = self.get_module_env(top_module_name)
                        module_alias = top_module_name
                    linear[module_alias] = module_env
            case _:
                self.diagnostics.append(
                    UnsupportedExprWarning(node, filename=self.current_file_path)
                )
        node.__context__ = context
        return ret_env

    def update_namespaces(self, module_name) -> str:
        name_tokens = module_name.split(".")
        # Now, we update
        for i in range(len(name_tokens) - 2, -1, -1):
            to_update_name = ".".join(name_tokens[: i + 1])
            to_update_env = self.get_module_env(to_update_name)
            to_add_name = name_tokens[i + 1]
            to_add_module = self.get_module_env(f"{to_update_name}.{to_add_name}")
            to_update_env[to_add_name] = to_add_module
        return name_tokens[0]

    def get_module_env(self, module_name: str) -> Environment:
        previous_file_path = self.current_file_path

        if module_name in self.file_paths:
            self.current_file_path = self.file_paths[module_name]

        try:
            if module_name not in self.namespaces:
                if module_name.startswith("tyger"):
                    if module_name.endswith("types"):
                        module_env = self.type_system.get_types()
                    else:
                        module_env = {}
                elif module_name == "typing":
                    module_env = self.type_system.get_typing_types()
                else:
                    try:
                        if self.deps is not None:
                            module = self.deps[module_name]
                            # Try to get the file path for this module from deps
                            if hasattr(module, "filename") and getattr(
                                module, "filename", None
                            ):
                                self.file_paths[module_name] = getattr(
                                    module, "filename"
                                )
                                self.current_file_path = getattr(module, "filename")

                            module_env = self.type_check_stmts(
                                module.body, package_name=module_name
                            )
                        else:
                            module_env = {}
                    except (KeyError, TypeError):
                        # Module not found in dependencies, treat as empty module
                        module_env = {}
                self.namespaces[module_name] = module_env
            else:
                module_env = self.namespaces[module_name]

            return module_env
        finally:
            self.current_file_path = previous_file_path

    def type_check_stmts(
        self,
        stmts: list[ast.stmt],
        linear: Environment = None,
        context: Context = None,
        package_name="",
    ) -> Environment:
        l = linear or {}
        context = context or self.type_system.get_initial_context()
        """
         (1) collect class Names, this means that type_check_stmts must be called with a namespace prefix
         (2) collect signatures
         (3) type check every class first to compute the spec of every class. How to choose the right order?
         For instance:
         class A:
             def foo(self, x: B):
                 self.a = x.b 
         class B:
             def foo(self, x: A):
                 self.b = x.a
         Maybe use an inference algorithm that collect constrains and then solve them. 
         (4) then type check the rest using the Names of classes as input.
        """

        # signatures = self.collect_signatures(stmts)
        func_defs: list[ast.FunctionDef] = []
        for st in stmts:
            l = self.type_check_stmt(st, {**l}, context, package_name)
            match st:
                case ast.FunctionDef():
                    func_defs.append(st)

        # Now we check function bodies
        for func in func_defs:
            body = func.body
            args = func.args.args
            dom, cod = get_args(func.__type__)
            arg_env = {arg.arg: typ for arg, typ in zip(args, dom)}
            assigned = self.collect_assigned_vars(func.body)
            func_body_env = {k: v for k, v in l.items() if k not in assigned}
            func_body_env.update(arg_env)

            func_context = func.__context__
            self.type_check_stmts(
                body, func_body_env, func_context.taint_context(func, cod), package_name
            )

        return l

    def collect_signatures(self, nodes: list[ast.stmt]) -> dict[str, type]:
        """
        Collects function signatures

        """
        signatures: dict[str, type] = {}
        for node in nodes:
            match node:
                case ast.FunctionDef(name, args, body, returns):
                    ty, _ = self.function_signature(node)
                    signatures[name] = ty
                case ast.ClassDef(name, bases, keywords, body, decorator_list):
                    ty = Callable[[], TypeName(name)]
                    for b in body:
                        match b:
                            case ast.FunctionDef("__init__", args, body, returns):
                                functype, _ = self.function_signature(b)
                                dom, cod = get_args(functype)
                                # we skip the self type
                                ty = Callable[[*dom[1:]], TypeName(name)]

                    signatures["Stream"] = ty
        return signatures

    def function_signature(
        self, node: ast.FunctionDef, linear: Environment, context: Context
    ) -> tuple[type, Environment]:
        env: Environment = {}
        tys: list[type] = []
        default_type = self.type_system.get_default_type()
        for a in node.args.args:
            ty: type = default_type
            if a.annotation:
                ann_type = self.type_check_expr(a.annotation, linear, context)
                ty = self.get_type_from_annotation(a.annotation)
            env[a.arg] = ty
            tys.append(ty)
        cod = self.type_system.get_cod_type_from_annotation(
            self.get_type_from_annotation(node.returns)
            if node.returns
            else default_type
        )

        return Callable[[*tys], cod], env

    def get_type_from_annotation(self, a: ast.expr) -> type:
        # type = parse_type(eval(ast.unparse(a), {**typing.__dict__, **globals()}))
        try:
            # Check if this is a Union or Optional type and emit warning
            if isinstance(a, ast.Subscript):
                if isinstance(a.value, ast.Name) and a.value.id in ["Union", "Optional"]:
                    self.diagnostics.append(
                        UnsupportedTypeWarning(
                            a,
                            f"Union and Optional types are not fully supported: {ast.unparse(a)}",
                            self.current_file_path
                        )
                    )
                elif isinstance(a.value, ast.Attribute) and a.value.attr in ["Union", "Optional"]:
                    self.diagnostics.append(
                        UnsupportedTypeWarning(
                            a,
                            f"Union and Optional types are not fully supported: {ast.unparse(a)}",
                            self.current_file_path
                        )
                    )
            
            t = self.type_system.parse_type(a)
            # type = self.type_system.parse_type(eval(ast.unparse(a), {**typing.__dict__, **globals()}))
            # print("returing", type)
            return t
        except Exception as e:
            # print(ast.dump(a, indent=2))
            # Fallback to unknown type for unsupported annotations
            return self.type_system.get_default_type()

    def check_consistency(
        self, expected_type: type | tuple | None, actual_type, node: ast.AST
    ):
        if expected_type is None:
            return
        match expected_type:
            case tuple():
                # In this case, we need to check each element consistency
                a_types = self.type_system.unwrap_value_type(
                    actual_type, len(expected_type)
                )
                if len(a_types) != len(expected_type):
                    self.diagnostics.append(
                        ArityMismatchError(
                            node,
                            len(expected_type),
                            len(a_types),
                            self.current_file_path,
                        )
                    )
                    return  # Return early to avoid further checks that might cause errors
                for exp, act in zip(expected_type, a_types):
                    self.check_consistency(exp, act, node)
            case _:
                if not self.type_system.consistent(actual_type, expected_type):
                    raise TypeMismatchError(node, actual_type, expected_type)

    def run(self, node: ast.Module, **kwargs) -> tuple[ast.Module, dict[str, Any]]:
        # TODO: check if it is necessary
        self.deps = kwargs.get("dependencies", {})
        self.diagnostics = kwargs.get("diagnostics", [])
        self.namespaces: dict[str, dict] = {}

        # We add the type system to the available namespaces
        types_module_name = self.type_system.__module__
        types_namespace = self.type_system.get_types()
        self.namespaces[types_module_name] = types_namespace

        try:
            self.type_check_stmts(node.body)
        except CriticalTypeCheckError as e:
            self.diagnostics.append(e)

        kwargs["diagnostics"] = self.diagnostics
        return node, kwargs
