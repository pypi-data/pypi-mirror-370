import functools
import types
from abc import ABC
from types import GenericAlias
from typing import get_args

from tyger.discipline.types import TypeSystem


class unk:
    pass


class tslice:
    pass


class TypeName(object):
    def __init__(self, name):
        self.name = name
        self.__qualname__ = "TypeName"

    def __repr__(self):
        return f"'{self.name}"

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        match other:
            case TypeName():
                return self.name == other.name
            case _:
                return False


class BaseTypeSystem(TypeSystem, ABC):
    def get_default_type(self):
        return unk

    def check_slice_type(self, value_type, slice_type):
        match value_type.__qualname__:
            case list.__qualname__:
                if (
                    slice_type.__qualname__ != tslice.__qualname__
                    and not self.consistent(slice_type, int)
                ):
                    raise TypeError("Expected int or slice, got {slice_type}")
            case dict.__qualname__:
                expected_key = get_args(value_type)[0]
                if not self.consistent(expected_key, slice_type):
                    raise TypeError(
                        "Expected key of type {expected_key}, got {slice_type}"
                    )

    def get_inner_type(self, ty):
        match ty.__qualname__:
            case unk.__qualname__:
                return unk
            case tuple.__qualname__:
                return functools.reduce(self.gjoin, get_args(ty))
            case list.__qualname__:
                return get_args(ty)[0]
            case dict.__qualname__:
                return get_args(ty)[1]

    def unwrap_value_type(self, actual_type, size) -> tuple:
        match actual_type.__qualname__:
            case unk.__qualname__:
                a_types = (unk,) * size
            case list.__qualname__:
                a_types = (get_args(actual_type)[0],) * size
            case tuple.__qualname__:
                a_types = get_args(actual_type)
            case dict.__qualname__:
                a_types = (get_args(actual_type)[1],) * size

        return a_types

    def get_slice_type(self):
        return tslice

    def get_domain(self, t: GenericAlias) -> type | GenericAlias:
        match t.__qualname__:
            case list.__qualname__:
                return int
            case dict.__qualname__:
                return get_args(t)[0]

    def get_default_dom_cod(self, n_args):
        arg_types = [unk for _ in range(n_args)]
        return arg_types, unk

    def get_types(self) -> dict[str, type | GenericAlias]:
        return {"unk": type}

    def get_typing_types(self) -> dict[str, type | GenericAlias]:
        return {
            "Callable": GenericAlias,
            "List": GenericAlias,
            "Dict": GenericAlias,
            "Tuple": GenericAlias,
            "Any": type,
            "Union": GenericAlias,
            "Optional": GenericAlias,
        }

    def check_annotation_type(self, ret_ann_type):
        match ret_ann_type.__qualname__:
            case type.__qualname__ | types.GenericAlias.__qualname__:
                return True
            case _:
                return False

    def get_builtin_types(self):
        return {
            "int": type,
            "str": type,
            "float": type,
            "dict": types.GenericAlias,
            "list": types.GenericAlias,
            "tuple": types.GenericAlias,
            "bool": type,
        }
