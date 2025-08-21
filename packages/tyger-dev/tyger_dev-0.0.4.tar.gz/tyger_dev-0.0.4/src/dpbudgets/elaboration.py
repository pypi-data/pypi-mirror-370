from typing import *
from ast import *
import typing

class unk:
    pass

class DP:
    pass


class Environment:
    pass



def parse_type(t: type) -> type:
    """
    This function parses a type
    :param t: the type to be parsed
    :return: the parsed type
    """
    match t:
        #now is safe to use __qualname__!
        case _ if t.__qualname__ == Callable.__qualname__:
            dom, cod = get_args(t)
            return Callable[[*map(parse_type, dom)], parse_type(cod)]
        case tuple():
            return tuple[map(parse_type, get_args(t))]
        case list():
            return list[map(parse_type, get_args(t))]
        case _:
            return t

def get_type_from_annotation(a: expr) -> type:
    return parse_type(eval(unparse(a), {**typing.__dict__, **globals()}))



def function_signature(node: FunctionDef) -> tuple[type, Environment]:
    env: Environment = {}
    tys: list[type] = []
    for a in node.args.args:
        ty: type = unk
        if a.annotation:
            ty = get_type_from_annotation(a.annotation)
        env[a.arg] = ty
        tys.append(ty)
    cod = get_type_from_annotation(node.returns) if node.returns else unk

    return Callable[[*tys], cod], env

def collect_signatures(nodes: list[stmt]) -> dict[str, type]:
    signatures: dict[str, type] = {}
    for node in nodes:
        match node:
            case FunctionDef(name, args, body, returns):
                ty, _ = function_signature(node)
                signatures[name] = ty

    return signatures


def type_check_expr(node: Expr, env: Environment = {}) \
        -> tuple[type, AST]:
    match node:
        case Name(id):
            t = env[id] if id in env.keys() else None
            if not t:
                raise TypeException(f"Unknown variable: {id}")
            return t, node
        case Constant(value):
            t = type_of(value)
            return t, node
        case Tuple(elts, ctx):
            tys = []
            elts_p = []
            for e in elts:
                ty, iterp = type_check_expr(e, env, context.no_expected())
                tys.append(ty)
                elts_p.append(iterp)
            #print("tuple", lineno, col_offset)
            return tuple[*tys], Tuple(elts_p, ctx)
        case Lambda(args, body):
            # we use unknown type, unless we are expecting a function type
            if context and context.expected:
                dom, _ = get_args(context.expected)
                if len([unk for _ in args.args]) < len(dom):
                    raise TypeException(f"Type mismatch, invalid argument size: {len([unk for _ in args.args])} != {len(dom)}")
            dom, cod = get_args(context.expected) if context and context.expected else ([unk for _ in args.args], unk)
            if len(dom) < len(args.args):
                dom.extend([unk]*(len(args.args)-len(dom)))
            local: dict[str, type] = {x.arg: ty for x, ty in zip(args.args, dom)}
            #print(local)
            ty, iterp = type_check_expr(body, {**env, **local}, context.taint_context(node, cod))
            return Callable[[*dom], cod], Lambda(args, iterp)

        case Call(func, args, keywords):
            #print(dump(node, indent=4))
            # print(f"looking for func={func}")

            envs = {**default_types, **env}
            match func:
                case Name():
                    if func.id in envs.keys():
                        callable = envs[func.id]
                        dom, cod = extract_dom_simple_cod(callable)
                        #we complete the dom type with unknown types in case there is not enough information about all arguments
                        if len(args)>len(dom):
                            dom = dom + [unk for _ in range(len(args)-len(dom))]
                        argsp = []
                        for pair in zip(dom, args):
                            domty, arg = pair
                            #print(f"Typechecking {dump(arg )} with {domty}")

                            _, argp = type_check_expr_to_type(arg, env, domty, context.no_expected(), ErrorLocation(node.lineno, node.col_offset))
                            #if primitive then we unwrap the values of the arguments to avoid problems
                            if func.id in default_types.keys():
                                argp = unwrap_value_to_ast(argp)
                            if func.id in renamings.keys():
                                func.id = renamings[func.id]
                            argsp.append(argp)

                        return cod, to_call_to_ast(func, argsp, keywords, context, callable)
                    else:
                        #print("about to return empty")
                        #transform the arguments
                        argsp = []
                        for arg in args:
                            _, argp = type_check_expr(arg, env, context.no_expected())
                            argsp.append(argp)
                        return None, Call(func, argsp, keywords)
                case Attribute(value, attr, ctx):
                    vty, vp = type_check_expr(value, envs, context.no_expected())
                    argsp = []
                    for arg in args:
                        _, argp = type_check_expr(arg, env, context.no_expected())
                        argsp.append(argp)
                    return unk, Call(Call(Attribute(Name('Wrapper', Load()), '__get_attr__', ctx), [vp, Constant(attr)], keywords = []), argsp, keywords)
                    vty, vp = type_check_expr(value, envs, context.no_expected())
                    #print("vty", vty)
                    raise Exception(f"Unsupported operation: {node}")
        case BinOp(left, op, right):
            lty, lb = type_check_expr(left, env, context.no_expected())
            rty, rb = type_check_expr(right, env, context.no_expected())
            ty = type_of_bin_primitive(op, lty, rty)
            dom, cod = extract_dom_simple_cod(ty)
            if not lty == dom[0]:
                ev = interior(lty, dom[0])
                lb = cast_to_ast(lb, ev)
            if not rty == dom[1]:
                ev = interior(rty, dom[1])
                rb = cast_to_ast(rb, ev)
            return cod, BinOp(lb, op, rb)

        case Compare(left, ops, comparators):
            lty, lb = type_check_expr(left, env, context.no_expected())
            rty, rb = type_check_expr(comparators[0], env, context.no_expected())
            ty = type_of_bin_primitive(ops[0], lty, rty)
            dom, cod = extract_dom_simple_cod(ty)
            ev = interior(lty, dom[0])
            lb = cast_to_ast(lb, ev)
            ev = interior(rty, dom[1])
            rb = cast_to_ast(rb, ev)
            return cod, Compare(lb, ops, [rb])

        case UnaryOp(op, operand):
            vty, iterp = type_check_expr(operand, env, context.no_expected())
            ty = type_of_un_primitive(op, vty)
            dom, cod = extract_dom_simple_cod(ty)
            if type(op) is type(Not()):
                return cod, not_to_ast(iterp)
            if not vty == dom[0]:
                ev = interior(vty, dom[0])
                iterp = cast_to_ast(iterp, ev)
            return cod, UnaryOp(op, iterp)
        case List(elts, ctx):
            #print("expected", expected)
            #we decide to wrap the list based on the expected type if there is any.
            wrapping_func = lambda x: x
            ty = None
            #first if the expected type is not a list, we raise an exception
            if context.expected:
                if context.expected.__qualname__ != list.__qualname__:
                    raise TypeException(f"Type mismatch: {context} != list")
                tyargs = get_args(context.expected)
                ty = tyargs[0] if len(tyargs)>0 else unk


            type_and_values = []
            for e in elts:
                vty, iterp = type_check_expr(e, env, context.no_expected())
                type_and_values.append([vty, iterp])
                #if not expected type, infer the type of the list
                if not context.expected:
                    if not ty:
                        ty = vty
                    else:
                        #print("gjoin between ", ty, vty)
                        ty = gjoin(ty, vty)

            #now we wrap each element if necessary
            elts_p = []
            for tv in type_and_values:
                vty, iterp = tv

                if not consistent(vty, ty):
                    raise TypeException(f"Type mismatch: {vty} != {ty}")
                elif vty != ty:
                    ev = interior(vty, ty)
                    iterp = cast_to_ast(iterp, ev)
                elts_p.append(iterp)

            return list[ty], List(elts_p, ctx)

        case Subscript(value, slice, ctx):
            vty, iterp = type_check_expr(value, env, context.no_expected())
            if vty.__qualname__ != list.__qualname__ and vty.__qualname__ != tuple.__qualname__:
                raise TypeException(f"Type mismatch: {vty} != list")

            sty, sb = type_check_expr(slice, env, context.no_expected())

            if sty.__qualname__ != tslice.__qualname__ and not consistent(sty, int):
                raise TypeException(f"Expected slice or integer, got: {sty}")
            #if not a slice, then it must be an integer
            elif sty.__qualname__ != tslice.__qualname__ and sty != int:
                ev = interior(sty, int)
                sb = cast_to_ast(sb, ev)
            sb = unwrap_value_to_ast(sb)
            #here we are assuming that the value is a list or a tuple
            args = get_args(vty)
            ty = args[0] if vty.__qualname__ == list.__qualname__ else unk
            return ty, Subscript(iterp, sb, ctx)
        case Slice(lower, upper, step):
            lowerp = None
            upperp = None
            stepp = None
            if lower:
                _, lb = type_check_expr_to_type(lower, env, int, context.no_expected())
                lowerp = unwrap_value_to_ast(lb)
            if upper:
                _, ub = type_check_expr_to_type(upper, env, int, context.no_expected())
                upperp = unwrap_value_to_ast(ub)
            if step:
                _, sb = type_check_expr_to_type(step, env, int, context.no_expected())
                stepp = unwrap_value_to_ast(sb)
            return tslice, Slice(lowerp, upperp, stepp)
        case ListComp(elt, generators):
            menv = {}
            generatorsp = []
            ifsp = []
            for g in generators:
                match g:
                    case comprehension(target, iter, ifs, is_async):

                        ty, iterp = type_check_expr(iter, env, context.no_expected())
                        #print("typing ", unparse(iter), ty, env)
                        inner_ty = unk
                        if not consistent(ty, list[unk]):
                            raise TypeException(f"Type mismatch: {ty} != list")
                        elif ty.__qualname__ == unk.__qualname__:
                            iterp = cast_to_ast(iterp, list[unk])
                        else:
                            inner_ty = get_args(ty)[0]
                        iterp = unwrap_value_to_ast(iterp)
                        menv[target.id] = inner_ty

                        if len(ifs) > 0:
                            #first we transform multiple ifs in a single if
                            ifp = BoolOp(And(), ifs) if len(ifs) > 1 else ifs[0]
                            #then we transform it
                            _, ifp = type_check_expr(ifp, {**env, **menv}, context.no_expected())
                            #and wrap the condition so it may propagate evidences
                            ifsp = [list_comp_if_to_ast(ifp)]

                        generatorsp.append(comprehension(target, iterp, ifsp, is_async))
                    case _:
                        raise Exception(f"Unsupported generator: {g}")
            vty, eltp = type_check_expr(elt, {**env, **menv}, context.no_expected())
            eltp = cast_to_ast(eltp, interior(vty, vty))
            return list[vty], list_comp_to_ast(eltp, generatorsp, ifsp) #ListComp(eltp, generatosp)
        case BoolOp(op, values):
            type_and_values = []
            valuesp = []
            ty = None
            for v in values:
                vty, vp = type_check_expr(v, env, context.no_expected())
                type_and_values.append([vty, vp])
                ty = vty if not ty else gjoin(ty, vty)
            #cast every element to the inferred type
            for tav in type_and_values:
                valuesp.append(cast_to_ast(tav[1], interior(tav[0], ty)))

            return ty, bool_op_to_ast(op, valuesp)
        case Attribute(value, attr, ctx):
            vty, vp = type_check_expr(value, env, context.no_expected())
            #ty = get_type_of_attr(vty, attr)
            ty = unk
            return ty, Call(Attribute(Name('Wrapper', Load()), '__get_attr__', ctx), [vp, Constant(attr)], keywords = [])
            #return ty, Attribute(vp, attr, ctx)
        case _:
            raise Exception(f"Unsupported expression: {node}")



def type_check_stmt(node: stmt, linear: Environment) -> tuple[Environment, list[AST]]:
    match node:
        case Expr(value):
            _, b = type_check_expr(value, linear, context)
            return linear, [Expr(b)]
        case FunctionDef(name, args, body, returns=returns):
            ty, vars = function_signature(node)
            dom, cod = get_args(ty)
            #print("context",context)
            linear[name] = ty
            _, node.body = type_check_stmts(body, {**linear, **vars}, context.taint_context(node, cod))
            return linear, [node]
        case Assign(targets, value):

            #the variable may be already initialized with a type. We should use that
            exp_type = None
            prev_val = Constant(None)
            for t in targets:
                match t:
                    case Name(id):
                        if id in linear.keys():
                            exp_type = linear[id]
                            prev_val = Name(id, Load())
                    case Attribute(v, attr, ctx):
                        #TODO: what about exp_type
                        prev_val = Attribute(v, attr, Load())
                    case Tuple(elts, ctx):
                        tys = []
                        prev_vals = []
                        for e in elts:
                            if e.id in linear.keys():
                                tys.append(linear[e.id])
                                prev_vals.append(Name(e.id, Load()))
                            else:
                                tys.append(None)
                                prev_vals.append(Constant(None))
                        exp_type = tuple[*tys]
                        prev_val = Tuple(prev_vals, Load())
            """
            We could have an assignment of the form
            x,y = (1,2)
            and one only x is initialized, therefore exp_type = tuple[int, None]
            therefore we infer the type and we unify exp_type with the inferred type, prioritizing exp_type
            """
            vty, b = type_check_expr(value, linear, context.taint_context(node, exp_type))
            ty = unify(vty, exp_type)

            typ = context.update_type(node, ty)
            #print(node, "has type", typ)
            for t in targets:
                match t:
                    case Name(id):
                        if not consistent(vty, typ):
                            raise TypeException(f"Type mismatch: {vty} != {typ}")
                        elif vty != typ:
                            ev = interior(vty, typ)
                            b = cast_to_ast(b, ev, ErrorLocation(node.lineno, node.col_offset))
                        linear[id] = typ
                    case Attribute(value, attr, ctx):
                        #TODO
                        pass
                        #b = cast_to_ast(b, ev, ErrorLocation(node.lineno, node.col_offset))
                    case Tuple(elts, ctx):
                        #print(typ)
                        #TODO: tuples
                        tys = get_args(typ)
                        if len(tys) != len(elts):
                            raise TypeException(f"Type mismatch: {vty} != {tys}")
                        _, b = type_check_expr_to_type(b, linear, typ, context, ErrorLocation(node.lineno, node.col_offset))
                        for (e, ty) in zip(elts, tys):
                            match e:
                                case Name(id):
                                    linear[id] = ty
                                case _:
                                    raise Exception(f"Unsupported node: {e}")
            return linear, to_assign_to_ast(targets, typ, b, context, prev_val)

        case AnnAssign(target, annotation, value, simple):
            #return linear, [node]
            match target:
                case Name(id):
                    #print("an assign ", id)
                    ty = get_type_from_annotation(annotation)
                    #print("type from annotation ", ty)
                    typ = context.update_type(node, ty)
                    prev_val = Name(id, Load()) if id in linear.keys() else Constant(None)
                    #print("prev value for ", id, prev_val)
                    # we pass the annotated type to the expression in case we need to use it to infer the type of an iterable.
                    #print(dump(node))
                    _, b = type_check_expr_to_type(value, linear, typ, context.taint_context(node, ty), ErrorLocation(node.lineno, node.col_offset))
                    #vty, b2 = type_check_expr(value, linear, context.update_context(node, ty))

                    valuep = b
                    linear[id] = typ
                    return linear, to_ann_assign_to_ast(target, annotation, typ, valuep, simple, context, prev_val)
                            #[AnnAssign(target, annotation, intercept_assign(context, valuep, typ, ev_expected), simple)])

        case Return(value):
            ty, b = type_check_expr(value, linear, context)
            ev_expected = None
            exp = context.expected
            typ = context.update_type(node, ty)
            if exp and not consistent(typ, exp):
                raise TypeException(f"Type mismatch: {typ} != {exp}")
            elif exp and typ != exp:
                ev = interior(typ, exp)
                b = cast_to_ast(b, ev, ErrorLocation(node.lineno, node.col_offset))
            else:
                ev_expected = interior(exp, exp)

            return linear, to_return_to_ast(b, ev_expected)
        case If(test, body, or_else):
            ty, b = type_check_expr(test, linear, context)
            contextp = context.taint_context(node, ty)
            #we make a copy of the linear environment as branches should not modify typing information of variables in scope. This is not true!! FIXED
            l, bodyp = type_check_stmts(body, linear, contextp)
            l, orelsep = type_check_stmts(or_else, l, contextp)
            return l, to_ite_to_ast(b, bodyp, orelsep)
        case While(test, body, or_else):
            ty, testp = type_check_expr(test, linear, context)
            contextp = context.taint_context(node, ty)
            l, bodyp = type_check_stmts(body, linear, contextp)
            l, orelsep = type_check_stmts(or_else, l, contextp)
            return l, to_while_to_ast(testp, bodyp, orelsep)
        case For(target, iter, body, or_else):
            ty, iterp = type_check_expr(iter, linear, context)
            inner_ty = unk
            if not consistent(ty, list[unk]):
                raise TypeException(f"For statement is expecting an iterable, but received: {ty}")
            elif ty.__qualname__ == unk.__qualname__:
                iterp = cast_to_ast(iterp, list[unk])
            else:
                inner_ty = get_args(ty)[0]
            linear[target.id] = inner_ty
            contextp = context.taint_context(node, ty)
            l, bodyp = type_check_stmts(body, linear, contextp)
            l, orelsep = type_check_stmts(or_else, l, contextp)
            return l, for_to_ast(target, iterp, bodyp, orelsep)
        case AugAssign(target, op, value):
            nodep = Assign([target], BinOp(Name(target.id, Load()), op, value))
            nodep.lineno = node.lineno
            nodep.col_offset = node.col_offset
            return type_check_stmt(nodep, linear, context)
        case Pass():
            return linear, [Pass()]
        case ClassDef(name, bases, keywords, body, decorator_list):
            if len(bases) > 0:
                raise TypeException(f"Unsupported operation: {node} for nont-empty bases")
            else:
                linear, node.body = type_check_stmts(body, linear, context)
                return linear, [node]
        case _:
            raise Exception(f"Unsupported statement: {node}")


def type_check_stmts(stmts: list[stmt], linear: Environment = {}) -> tuple[Environment, list[AST]]:
    l = linear
    bodyp = []

    signatures = collect_signatures(stmts)

    for stmt in stmts:
        l, b = type_check_stmt(stmt, {**l, **signatures}, context)
        bodyp.extend(b)
    return l, bodyp

def type_check(node: AST, program: str | None = None) -> tuple[Environment, AST]:

    linear: Environment = {}
    match node:
        case Module(body, type_ignores):
            l, bodyp = type_check_stmts(body, {**linear})
            return l, Module(bodyp, type_ignores)
        case _:
            raise Exception(f"Unsupported node: {node}")
    return (None, linear, node)  # FIX: unreachable



if __name__ == "__main__":
    program = """
def f() -> DP[float]:
    with consuming(40): laplace_mechanism(10, 1)
    with consuming(60): laplace_mechanism(10, 1)

def laplace_mechanism(x: float, sens: float) -> DP[float]:
    with spend():
        return x + np.random.laplace(loc=0, scale=sens / epsilon)
        
with budget(10):
    with consuming(50):
        [laplace_mechanism(x, 1) for x in PDIterator(range(0,10), lambda i,n: 1/pow(2,n-i))]
    with consuming(30):
        laplace_mechanism(10, 1)
    with consuming(10):
        f()

    """
    parsed_ast = parse(program)
    print(dump(parsed_ast, indent=2))
    env, b = type_check(parsed_ast, program)

