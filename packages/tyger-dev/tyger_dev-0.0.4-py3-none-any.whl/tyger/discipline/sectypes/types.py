from functools import reduce
import ast
from types import GenericAlias
from typing import Callable, Any, get_args

from tyger.discipline.base.types import BaseTypeSystem, unk, tslice, TypeName
from tyger.discipline.types import TypeException, Context


class label(object):
    pass


class Top(label):
    pass


class H(Top):
    pass


class M(H):
    pass


class L(M):
    pass


class Bot(L):
    pass


class CodType(object):
    """
    A Codype is a type that represents the return type of a function, the label of the function, and the minimum PC
    Example: Cod[L,M,H] represents a function that returns a value of type L, has label M, and requires a minimum PC of H
    """

    def __class_getitem__(cls, *args, **kwargs):  # real signature unknown

        params = args[0]
        if not isinstance(params, tuple):
            params = (params,)
        elif len(params) <= 0:
            args = ((unk, unk, unk),)
        elif len(params) <= 1:
            args = ((params[0], unk, unk),)
        elif len(params) <= 2:
            args = ((params[0], params[1], unk),)
        elif len(params) > 3:
            raise Exception("Too many arguments")
        return GenericAlias(cls, *args)


class SecurityTypeSystem(BaseTypeSystem):

    def type_of(self, v: Any) -> type:
        """
        This function returns the type of a value
        :param v: the value
        :return: the type of the value. Here we default to the lowest security level
        """
        return Bot

    def parse_type(self, t: ast.expr) -> type:
        """
        This function parses a type
        :param t: the type to be parsed
        :return: the parsed type
        """
        match t:
            case ast.Name(idx):
                match idx:
                    case L.__qualname__:
                        return L
                    case M.__qualname__:
                        return M
                    case H.__qualname__:
                        return H
                    case unk.__qualname__:
                        return unk
            case ast.Subscript(value, sl):
                match value.id:
                    case Callable.__qualname__:
                        dom_elts = sl.elts[0].elts
                        dom = (self.parse_type(_t) for _t in dom_elts)
                        cod = self.parse_type(sl.elts[1])
                        return Callable[[*dom], cod]

                    case CodType.__qualname__:
                        cod_args = (self.parse_type(typ) for typ in sl.elts)
                        return CodType[*cod_args]

        return None

    def consistent(self, a: type, b: type) -> bool:
        #print([a], [b])
        #print(f"Calling consistent on {a.__qualname__} and {b.__qualname__}")
        match (a.__qualname__, b.__qualname__):
            case (unk.__qualname__, _):
                return True
            case (_, unk.__qualname__):
                return True
            case (Callable.__qualname__, Callable.__qualname__):
                dom1, cod1 = get_args(a)
                dom2, cod2 = get_args(b)
                dom = reduce(lambda x, y: x and y, map(lambda p: self.consistent(p[0], p[1]), zip(dom2, dom1))) if len(
                    dom1) > 0 else True
                cod = self.consistent(cod1, cod2)
                length = len(dom1) == len(dom2) or dom1[-1].__qualname__ == unk.__qualname__ or dom2[
                    -1].__qualname__ == unk.__qualname__
                return length and dom and cod
            case (CodType.__qualname__, CodType.__qualname__):
                cod1, lbl1, pc1 = extract_cod_lbl_lat(a)
                cod2, lbl2, pc2 = extract_cod_lbl_lat(b)
                return self.consistent(cod1, cod2) and self.consistent(lbl1, lbl2) and self.consistent(pc2, pc1)
            case (tuple.__qualname__, tuple.__qualname__):
                left = get_args(a)
                right = get_args(a)
                return len(left) == len(right) and reduce(lambda x, y: x and y,
                                                          map(lambda p: self.consistent(p[0], p[1]),
                                                              zip(left, right)))
            case (list.__qualname__, list.__qualname__):
                left = get_args(a)
                right = get_args(b)
                return len(left) == len(right) and reduce(lambda x, y: x and y,
                                                          map(lambda p: self.consistent(p[0], p[1]),
                                                              zip(left, right)))

            case (_, _):
                return leq(a, b)
        return False

    def type_of_bin_primitive(self, op, lty: type, rty: type):
        """
        This function returns the type of a primitive operation given the types of the operands
        :param op: the operator
        :param lty: the left operand type
        :param rty: the right operand type
        :return: the type of the operation
        """
        return Callable[[lty, rty], CodType[static_join(lty, rty), Bot, Bot]]

    def type_of_un_primitive(self, op, ty: type):
        """
        This function returns the type of a primitive operation given the types of the operands
        :param op: the operator
        :param ty: the operand type
        :return: the type of the operation
        """
        return Callable[[ty], CodType[ty, Bot, Bot]]

    def get_cod_type_from_annotation(self, ty):
        """When typechecking signatures, we parse the codomain annotation and construct a complex cod type
        :param ty: the parsed codomain type from function signature annotation
        :return: the complex codomain type
        """
        match ty.__qualname__:
            case CodType.__qualname__:
                return ty
            case unk.__qualname__:
                return CodType[unk, unk, unk]
            case list.__qualname__:
                return CodType[*ty]
            case _:
                if issubclass(ty, label):
                    return CodType[ty]
                else:
                    raise Exception(f"Expected a CodType, got {ty}")

    def extract_func_type(self, ty):
        return extract_func_type(ty)

    def dom_cod(self, ty):
        match ty.__qualname__:
            case Callable.__qualname__:
                args = get_args(ty)
                cod, lbl, lat = extract_cod_lbl_lat(args[1])
                return args[0], self.gjoin(cod, lbl)
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
            case (a, b):
                match (a.__qualname__, b.__qualname__):
                    case (tuple.__qualname__, unk.__qualname__):
                        left = get_args(lty)
                        return self.unify(lty, tuple[unk] * len(left))
                    case (unk.__qualname__, tuple.__qualname__):
                        right = get_args(rty)
                        return self.unify(tuple[unk] * len(right), rty)
                    case (tuple.__qualname__, tuple.__qualname__):
                        left = get_args(lty)
                        right = get_args(rty)
                        if len(left) == len(right):
                            args = [self.unify(l, r) for l, r in zip(left, right)]
                            return tuple[*args]
                        else:
                            return unk
                    # TODO: cases for list
                    case (_, _):
                        return rty

    def get_types(self) -> dict[str, type | GenericAlias]:
        base = super().get_types()
        sec_types = {t: type for t in ["H", "M", "L"]}
        return {**base, **sec_types, "CodType": GenericAlias}

    def get_initial_context(self) -> "SecurityContext":
        return SecurityContext.initial()

    def gjoin(self, ty1, ty2):
        return gjoin(ty1, ty2)


def extract_func_type(ty):
    match ty.__qualname__:
        case Callable.__qualname__:
            return get_args(ty)
        case unk.__qualname__:
            return [unk], CodType[unk, unk, unk]
        case _:
            raise Exception(f"Expected a Callable, got {ty}")


def gjoin(a: type, b: type) -> type:
    match (a.__qualname__, b.__qualname__):
        case (Top.__qualname__, _) | (_, Top.__qualname__):
            return Top
        case (unk.__qualname__, _):
            return unk
        case (_, unk.__qualname__):
            return unk
        case (CodType.__qualname__, CodType.__qualname__):
            cod1, lbl1, pc1 = extract_cod_lbl_lat(a)
            cod2, lbl2, pc2 = extract_cod_lbl_lat(b)
            cod = gjoin(cod1, cod2)
            lbl = gjoin(lbl1, lbl2)
            pc = gjoin(pc1, pc2)
            return CodType[cod, lbl, pc]
        # case (CodType.__qualname__, _):
        #    cod, lbl, pc = extract_cod_lbl_lat(a)
        #    return CodType[cod, gjoin(lbl,b), pc]
        case (Callable.__qualname__, Callable.__qualname__):
            dom1, cod1 = get_args(a)
            dom2, cod2 = get_args(b)
            if len(dom1) == len(dom2):
                dom = map(lambda p: gjoin(p[0], p[1]), zip(dom2, dom1))
                cod = gjoin(cod1, cod2)
                return Callable[[*dom], cod]
            else:
                return unk
        case (Callable.__qualname__, _):
            dom, cod = get_args(a)
            cod, lbl, pc = extract_cod_lbl_lat(cod)
            return Callable[[*dom], CodType[cod, gjoin(lbl, b), pc]]

        # TODO: tuple and list must have a similar treatment
        case (tuple.__qualname__, tuple.__qualname__):
            left = get_args(a)
            right = get_args(a)
            if len(left) == len(right):
                return tuple[gjoin(left[0], right[0])]
            else:
                return unk
        case (list.__qualname__, list.__qualname__):
            left = get_args(a)
            right = get_args(a)
            if len(left) == len(right):
                return tuple[gjoin(left[0], right[0])]
            else:
                return unk

        case (aqn, bqn):
            if issubclass(a, b):
                return b
            elif issubclass(b, a):
                return a
            else:
                return unk  # This could be top as well
    return unk


def leq(a: type, b: type) -> bool:
    match (a.__qualname__, b.__qualname__):
        case (unk.__qualname__, _) | (_, unk.__qualname__):
            return True
        case (_, _):
            return issubclass(a, b)


def static_meet(a: type, b: type) -> type:
    if issubclass(a, b):
        return a
    elif issubclass(b, a):
        return b
    else:
        raise Exception(f"Cannot meet {a} and {b}")


def static_join(a: type, b: type) -> type:
    match (a.__qualname__, b.__qualname__):
        #adding unknown support for typing primitives
        case (unk.__qualname__, _):
            return b
        case (_, unk.__qualname__):
            return a
        case _:
            if issubclass(a, b):
                return b
            elif issubclass(b, a):
                return a
            else:
                raise Exception(f"Cannot join {a} and {b}")


def extract_lbl(ty):
    match ty.__qualname__:
        case CodType.__qualname__:
            _, lbl, _ = extract_cod_lbl_lat(ty)
            return lbl
        case Callable.__qualname__:
            _, cod = get_args(ty)
            _, lbl, _ = extract_cod_lbl_lat(cod)
            return lbl
        case _:
            return ty


def extract_cod_lbl_lat(ty):
    """
    This function extracts the simple codomain type, the label and the PC from a complex codomain type
    """
    match ty.__qualname__:
        case CodType.__qualname__:
            args = get_args(ty)
            if len(args) > 0:
                return get_args(ty) + (unk,) * (3 - len(args))
            else:
                return (unk, unk, unk)
        case unk.__qualname__:
            return (unk, unk, unk)
        case _:
            raise Exception(f"Expected a CodType, got {ty}")


class SecurityContext(Context):
    def __init__(self, expected: type | None, pc: type, join_type: type | None):
        self.expected = expected
        self.pc = pc
        self.join_type = join_type

    @classmethod
    def initial(cls):
        return cls(None, Bot, None)

    def no_expected(self):
        return SecurityContext(None, self.pc, self.join_type)

    def taint_context(self, node, ty: type) -> 'SecurityContext':
        """
        Get the context from a node and a type. In this simple case is just the expected type.
        At least it hast to have an expected type
        :param node: the node being type checked and/or elaborated
        :param ty: the type information of the node
        :return: the contextual information to be passed on the inner nodes
        """
        match node:
            case ast.FunctionDef():
                cod, lbl, pc = extract_cod_lbl_lat(ty)
                return SecurityContext(cod, pc, self.join_type)
            case ast.AnnAssign() | ast.Assign():
                return SecurityContext(ty, self.pc, self.join_type)
            case ast.Lambda():
                cod, lbl, pc = extract_cod_lbl_lat(ty)
                return SecurityContext(cod, pc, self.join_type)
            case ast.If():
                lbl = extract_lbl(ty)
                return SecurityContext(self.expected, gjoin(self.pc, lbl),
                                       gjoin(self.join_type, lbl) if self.join_type else lbl)
            case _:
                raise Exception(f"Node {node} not supported")

    def taint_type(self, node, ty):
        """
        Update the return type from the context. Here we join ty with the join_type from context
        :param node: the node
        :param ty: the return type
        :return: the updated return type
        """
        match node:
            case ast.Return():
                return gjoin(ty, self.join_type) if self.join_type else ty
            case ast.AnnAssign() | ast.Assign():
                if leq(self.pc, extract_lbl(ty)):
                    return ty
                else:
                    raise TypeException(f"Security error: PC {self.pc} is not less or equal than {extract_lbl(ty)}")
            case _:
                return ty
