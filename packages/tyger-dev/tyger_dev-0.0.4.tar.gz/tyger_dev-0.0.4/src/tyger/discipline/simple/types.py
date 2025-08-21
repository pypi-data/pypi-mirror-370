from functools import reduce
import ast
from typing import Callable, get_args, Any

from tyger.discipline.base.types import BaseTypeSystem, unk
from tyger.discipline.types import Context
from tyger.diagnostics.errors import NotFoundBinOpTypeError, NotFoundUnOpTypeError

primitives: dict[type, list[type]] = {
    type(ast.Add()): [
        Callable[[int, int], int],
        Callable[[float, float], float],
        Callable[[str, str], str],
    ],
    type(ast.Sub()): [Callable[[int, int], int], Callable[[float, float], float]],
    type(ast.Mult()): [Callable[[int, int], int], Callable[[float, float], float]],
    type(ast.Div()): [Callable[[int, int], int], Callable[[float, float], float]],
    type(ast.Not()): [Callable[[bool], bool]],
    type(ast.Lt()): [
        Callable[[int, int], bool],
        Callable[[float, float], bool],
        Callable[[str, str], bool],
    ],
    type(ast.Eq()): [
        Callable[[int, int], bool],
        Callable[[float, float], bool],
        Callable[[str, str], bool],
    ],
    type(ast.Gt()): [
        Callable[[int, int], bool],
        Callable[[float, float], bool],
        Callable[[str, str], bool],
    ],
    type(ast.LtE()): [
        Callable[[int, int], bool],
        Callable[[float, float], bool],
        Callable[[str, str], bool],
    ],
    type(ast.GtE()): [
        Callable[[int, int], bool],
        Callable[[float, float], bool],
        Callable[[str, str], bool],
    ],
    type(ast.USub()): [Callable[[int], int], Callable[[float], float]],
    type(ast.Mod()): [Callable[[int, int], int], Callable[[float, float], float]],
}


class SimpleTypeSystem(BaseTypeSystem):

    def type_of(self, v: Any) -> type:
        """
        This function returns the type of a value

        Args:
            v: the value to be checked
        Returns:
            The type of the value
        """
        return type(v)

    def gjoin(self, a: type, b: type) -> type:
        match (a.__qualname__, b.__qualname__):
            case (unk.__qualname__, _):
                return unk
            case (_, unk.__qualname__):
                return unk
            case (Callable.__qualname__, Callable.__qualname__):
                dom1, cod1 = get_args(a)
                dom2, cod2 = get_args(b)
                if len(dom1) == len(dom2):
                    dom = map(lambda p: self.gjoin(p[0], p[1]), zip(dom2, dom1))
                    cod = self.gjoin(cod1, cod2)
                    return Callable[[*dom], cod]
                else:
                    return unk
            case (tuple.__qualname__, tuple.__qualname__):
                left = get_args(a)
                right = get_args(a)
                if len(left) == len(right):
                    tys = [self.gjoin(l, r) for l, r in zip(left, right)]
                    return tuple[*tys]
                else:
                    return unk

            case (list.__qualname__, list.__qualname__):
                left = get_args(a)
                right = get_args(a)
                if len(left) == len(right):
                    return tuple[self.gjoin(left[0], right[0])]
                else:
                    return unk
            case (aqn, bqn):
                if aqn == bqn:
                    return a
                else:
                    return unk
        return unk

    # get the domain and simple cod type of a function type
    def dom_cod(self, ty):
        match ty.__qualname__:
            case Callable.__qualname__:
                return get_args(ty)
            case unk.__qualname__:
                return [unk], unk
            case _:
                raise Exception(f"Expected a Callable, got {ty}")

    def extract_iterable(self, ty):
        match ty.__qualname__:
            case list.__qualname__ | tuple.__qualname__:
                return ty
            case unk.__qualname__:
                # TODO: should we create an iterable class? how to know if its a list or a tuple?
                return list[unk]
            case _:
                return unk

    def unify(self, lty, rty):
        """prioritize type on the right"""
        match (lty, rty):
            case (None, _):
                return rty
            case (_, None):
                return lty
            case tuple(), tuple():
                return (self.unify(_l, _r) for _l, _r in zip(lty, rty))
            case (a, b):
                match (a.__qualname__, b.__qualname__):
                    case (tuple.__qualname__, unk.__qualname__):
                        left = get_args(lty)
                        return self.unify(lty, tuple[*((unk,) * len(left))])
                    case (unk.__qualname__, tuple.__qualname__):
                        right = get_args(rty)
                        return self.unify(tuple[*((unk,) * len(right))], rty)
                    case (tuple.__qualname__, tuple.__qualname__):
                        left = get_args(lty)
                        right = get_args(rty)
                        if len(left) == len(right):
                            args = [self.unify(l, r) for l, r in zip(left, right)]
                            return tuple[*args]
                        else:
                            return unk
                    case (_, _):
                        return rty

    def type_of_bin_primitive(self, op, lty, rty) -> Callable:
        """
        This function returns the type of a primitive operation given the types of the operands

        Args:
            op: the operator
            lty: the left operand type
            rty: the right operand type
        Returns:
            The type of the operation
        Raises:
            NotFoundOpTypeError: if no type is found for the operation
        """
        str_op = type(op)
        if str_op == type(ast.Eq):
            return Callable[[lty, rty], bool]
        if (
            str_op == type(ast.Add())
            and lty.__qualname__ == "list"
            and lty.__qualname__ == rty.__qualname__
        ):
            # The resulting list will have the join of both types as its type
            (t1,) = get_args(lty)
            (t2,) = get_args(rty)
            typ = self.gjoin(t1, t2)
            dom = [typ, typ]
            cod = typ
            return Callable[[*dom], cod]
            # if consistent(rty, dom[1]):
        if str_op in primitives.keys():
            for ty in primitives[str_op]:
                dom, cod = get_args(ty)
                if self.consistent(lty, dom[0]) and self.consistent(rty, dom[1]):
                    return ty

        raise NotFoundBinOpTypeError(op, lty, rty, str(str_op))

    def type_of_un_primitive(self, op, ty: type):
        """
        This function returns the type of a primitive operation given the types of the operands

        Args:
            op: the operator
            ty: the operand type
        Returns:
            The type of the operation
        """
        if type(op) is type(ast.Not()):
            return Callable[[ty], bool]
        if type(op) in primitives.keys():
            for fty in primitives[type(op)]:
                dom, cod = get_args(fty)
                # print(f"testing consistency between {vty} and {dom[0]}")
                if self.consistent(ty, dom[0]):
                    return fty
        else:
            raise NotFoundUnOpTypeError(op, ty, str(type(op)))

    def consistent(self, a: type, b: type) -> bool:
        # print(f"Calling consistent on {a} and {b}")
        # TODO: Al crear un list[Any], o list[List[int]] con tipos de typing dentro de list, no
        # funciona bien el get_args, porque no tiene __qualname__.
        # Si funciona con List[Callable[[Any], Any]]. No sé por qué
        
        # Handle None values gracefully (for unsupported types)
        if a is None or b is None:
            return True  # Treat None as compatible with everything (like unk)
            
        match (a.__qualname__, b.__qualname__):
            case (unk.__qualname__, _):
                return True
            case (_, unk.__qualname__):
                return True
            case (Callable.__qualname__, Callable.__qualname__):
                dom1, cod1 = get_args(a)
                dom2, cod2 = get_args(b)

                if len(list(zip(dom2, dom1))) > 0:
                    dom = (
                        reduce(
                            lambda x, y: x and y,
                            map(lambda p: self.consistent(p[0], p[1]), zip(dom2, dom1)),
                        )
                        if (len(dom1) > 0 and len(dom2) > 0)
                        else True
                    )
                else:
                    dom = True
                cod = self.consistent(cod1, cod2)
                length = (
                    len(dom1) == len(dom2)
                    or (
                        len(dom1) < len(dom2)
                        and dom1[-1].__qualname__ == unk.__qualname__
                    )
                    or (
                        len(dom2) < len(dom1)
                        and dom2[-1].__qualname__ == unk.__qualname__
                    )
                )
                return length and dom and cod
            case (tuple.__qualname__, tuple.__qualname__) | (
                list.__qualname__,
                list.__qualname__,
            ):
                left = get_args(a)
                right = get_args(b)
                return len(left) == len(right) and reduce(
                    lambda x, y: x and y,
                    map(lambda p: self.consistent(p[0], p[1]), zip(left, right)),
                )
            case (dict.__qualname__, dict.__qualname__):
                left_key, left_val = get_args(a)
                right_key, right_val = get_args(b)
                return self.consistent(left_key, right_key) and self.consistent(
                    left_val, right_val
                )
            case (aqn, bqn):
                return aqn == bqn
        return False

    def parse_type(self, t: ast.expr) -> type:
        """
        This function parses a type

        Args:
            t: the type to be parsed
        Returns:
            the parsed type
        """
        match t:
            case ast.Name(idx):
                match idx:
                    case int.__qualname__:
                        return int
                    case str.__qualname__:
                        return str
                    case bool.__qualname__:
                        return bool
                    case float.__qualname__:
                        return float
                    case unk.__qualname__:
                        return unk
                    case "Any":
                        return unk  # Treat Any as unknown type in our type system

            case ast.Subscript(value, sl):
                # Handle both ast.Name (Union) and ast.Attribute (typing.Union)
                type_name = None
                if isinstance(value, ast.Name):
                    type_name = value.id
                elif isinstance(value, ast.Attribute):
                    type_name = value.attr
                
                match type_name:
                    case Callable.__qualname__:
                        dom_elts = sl.elts[0].elts
                        dom = (self.parse_type(_t) for _t in dom_elts)
                        cod = self.parse_type(sl.elts[1])
                        return Callable[[*dom], cod]
                    case list.__qualname__ | "List":
                        inner = self.parse_type(sl)
                        return list[inner]
                    case tuple.__qualname__ | "Tuple":
                        inner = (self.parse_type(_t) for _t in sl.elts)
                        return tuple[*inner]
                    case dict.__qualname__ | "Dict":
                        dom = self.parse_type(sl.elts[0])
                        cod = self.parse_type(sl.elts[1])
                        return dict[dom, cod]
                    case "Union" | "Optional":
                        # For now, treat Union and Optional as unknown types
                        # TODO: Implement proper Union type support
                        return unk
            case _:
                raise Exception(f"Unsupported type: {t}")

        # match t:
        #     case ForwardRef():
        #         return TypeName(t.__forward_arg__)
        #     #now is safe to use __qualname__!
        #     case _ if t.__qualname__ == Callable.__qualname__:
        #         dom, cod = get_args(t)
        #         return Callable[[*map(self.parse_type, dom)], self.parse_type(cod)]
        #     case tuple():
        #         return tuple[map(self.parse_type, get_args(t))]
        #     case list():
        #         return list[map(self.parse_type, get_args(t))]
        #     case _:
        #         return t

    def get_cod_type_from_annotation(self, ty):
        """When typechecking signatures, we parse the codomain annotation and construct a complex cod type

        Args:
            ty: the codomain type from function signature annotation
        Returns:
            The complex codomain type
        """
        return ty

    def extract_func_type(self, ty):
        return self.dom_cod(ty)

    def get_initial_context(self) -> "Context":
        return SimpleContext.initial()


class SimpleContext(Context):
    def __init__(self, expected: type):
        self.expected = expected

    @classmethod
    def initial(cls):
        return cls(None)

    def no_expected(self):
        return SimpleContext(None)

    def taint_context(self, node, ty: type) -> "Context":
        """
        Get the context from a node and a type. In this simple case is just the expected type.
        At least it hast to have an expected type
        :param node: the node being type checked and/or elaborated
        :param ty: the type information of the node
        :return: the contextual information to be passed on the inner nodes
        """
        match node:
            case ast.FunctionDef():
                return SimpleContext(ty)
            case ast.AnnAssign():
                return SimpleContext(ty)
            case ast.Lambda():
                return SimpleContext(ty)
            case _:
                return self
                # raise Exception(f"Node {node} not supported")

    def taint_type(self, node, ty):
        """
        Update the return type from the context.

        Args:
            node: the node being type checked and/or elaborated
            ty: the type information of the node
        Returns:
            The updated return type
        """
        return ty


# Singleton
simple_type_system = SimpleTypeSystem()
