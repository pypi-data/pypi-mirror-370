import functools
import textwrap
from typing import Any, Callable

from tyger.discipline.evidence import Evidence, EvidenceFactory
from tyger.discipline.base.types import unk
from tyger.runtime.contextual_information import thlci


class ErrorLocation:
    def __init__(self, lineno: int = -1, col_offset: int = -1):
        self.lineno = lineno
        self.col_offset = col_offset

    def __str__(self):
        return f"line {self.lineno}, column {self.col_offset}"


class Wrapper:
    value: Any
    ev: Evidence

    def __init__(self, value: Any, ev: Evidence, lineno: int = -1, col_offset: int = -1):
        self.lineno = lineno
        self.col_offset = col_offset
        # print("initiating wrapper with value: ", value, " and evidence: ", ev)
        # if the type of the value is a wrapper, combine the two wrappers:
        if isinstance(value, Wrapper):
            self.value = value.value
            try:
                self.ev = value.ev.trans(ev)
            except Exception as e:
                if lineno >= 0:
                    lines = thlci.program.split("\n")
                    msg = f"""
                    at line {lineno}, column {col_offset}:
                    {lines[lineno - 1]}
                    """
                    e.add_note(textwrap.dedent(msg))
                raise

        # otherwise, trust that the value is correct for the given evidence
        else:
            self.value = value
            self.ev = ev

        # if the underlying value is a tuple or a list, we need to wrap each element
        if self.ev.is_tuple():
            evs = self.ev.ituple(self.ev)
            self.value = tuple(map(lambda x: Wrapper(x[0], x[1]), zip(self.value, evs)))
        elif self.ev.is_list():
            ev = self.ev.ilist(self.ev)
            self.value = list(map(lambda x: Wrapper(x, ev), self.value))
        elif self.ev.is_dict():
            dom_ev, cod_ev = self.ev.idict(self.ev)
            self.value = {Wrapper(key, dom_ev): Wrapper(val, cod_ev) for key, val in self.value.items()}

    @classmethod
    def wrap_each(cls, expr: Any, tup_ev: tuple | Evidence):

        # Check if we are unpacking or on a base case
        match tup_ev:
            case Evidence():  # Base case.
                return Wrapper(expr, tup_ev)
            case tuple():
                match expr:
                    case Wrapper():
                        # TODO: transitivity
                        return cls.wrap_each(expr.value, tup_ev)
                    case list():
                        if len(expr) != len(tup_ev):
                            raise ValueError("Unpack error")
                        return [Wrapper.wrap_each(e, ev) for e, ev in zip(expr, tup_ev)]
                    case tuple():
                        if len(expr) != len(tup_ev):
                            raise ValueError("Unpack error")
                        return tuple(Wrapper.wrap_each(e, ev) for e, ev in zip(expr, tup_ev))
                    case _:
                        # TODO: WHAT HERE?
                        return Wrapper(expr, tup_ev)

    @classmethod
    def join(cls, value: Any, ev: Evidence, *args):
        match value:
            case Wrapper():
                return cls(value.value, value.ev.join(ev, *args))
            case a:
                return cls(a, ev)  # Not sure about this one

    @classmethod
    def intercept_return(cls, value: Any, ev: Evidence | None = None, ev_fact: EvidenceFactory = None, *args):
        evs: list[Evidence] = thlci.evs

        if len(evs) <= 0:
            return value

        init = cls(value, ev) if ev else value
        init = Wrapper.join(init, functools.reduce(lambda x, y: x.join(y), evs), *args)
        return init

    @classmethod
    def intercept_assign(cls, value: Any, ev: Evidence | None = None, *args):
        evs: list[Evidence] = thlci.evs

        if len(evs) <= 0:
            return value
        init = cls(value, ev) if ev else value
        pc = functools.reduce(lambda x, y: x.join(y), evs)
        init = Wrapper.join(init, pc, *args)
        # TODO: how to refactor?
        pc.custom_assign_runtime_check(value, ev, pc, *args)
        return init

    def __repr__(self):
        return f"({self.ev} {self.value})"

    def binop(self, other: Any, op: Callable[[Any, Any], Any],
              ev_op: Callable[[Evidence, Evidence], Evidence] = lambda x, y: x):

        match other:
            case Wrapper():
                return Wrapper(op(self.value, other.value), ev_op(self.ev, other.ev))
            case int() | float() | complex():
                return Wrapper(op(self.value, other), ev_op(self.ev, self.ev))
            case _:
                return Wrapper(op(self.value, other), ev_op(self.ev, self.ev))

    def rbinop(self, other: Any, op: Callable[[Any, Any], Any],
               ev_op: Callable[[Evidence, Evidence], Evidence] = lambda x, y: x):
        match other:
            case Wrapper():
                return Wrapper(op(other.value, self.value), ev_op(self.ev, other.ev))
            case int() | float() | complex():
                return Wrapper(op(other, self.value), ev_op(self.ev, self.ev))
            case _:
                return Wrapper(op(other, self.value), ev_op(self.ev, self.ev))

    def __add__(self, other):
        return self.binop(other, lambda x, y: x + y, lambda x, y: x + y)

    def __sub__(self, other):
        return self.binop(other, lambda x, y: x - y, lambda x, y: x - y)

    def __mul__(self, other):
        return self.binop(other, lambda x, y: x * y, lambda x, y: x * y)

    def __lt__(self, other):
        return self.binop(other, lambda x, y: x < y, lambda x, y: x < y)

    def __le__(self, other):
        return self.binop(other, lambda x, y: x <= y, lambda x, y: x <= y)

    def __gt__(self, other):
        return self.binop(other, lambda x, y: x > y, lambda x, y: x > y)

    def __ge__(self, other):
        return self.binop(other, lambda x, y: x >= y, lambda x, y: x >= y)

    def __eq__(self, other):
        return self.binop(other, lambda x, y: x == y, lambda x, y: x.eq(y))

    def __ne__(self, other):
        return self.binop(other, lambda x, y: x != y, lambda x, y: x != y)

    def __mod__(self, other):
        return self.binop(other, lambda x, y: x % y, lambda x, y: x % y)

    def __radd__(self, other):
        # for lists this is not commutative
        return self.rbinop(other, lambda x, y: x + y, lambda x, y: x + y)

    def __rsub__(self, other):
        return self.rbinop(other, lambda x, y: x - y, lambda x, y: x - y)

    def __rmul__(self, other):
        return self.rbinop(other, lambda x, y: x * y, lambda x, y: x * y)

    def __neg__(self):
        return Wrapper(-self.value, -self.ev)

    def __call__(self, *other):
        dom, cod = self.ev.idomcod()
        if len(other) > len(dom):
            dom.extend([self.ev.interior(unk, unk)] * (len(other) - len(dom)))
        wraps = [Wrapper(x, y) for x, y in zip(other, dom)]
        return Wrapper(self.value(*wraps), cod, lineno=self.lineno, col_offset=self.col_offset)

    def __getitem__(self, item):
        # it's ok to drop the evidence in iterables, as the evidence its already pushed inside each value.
        return self.value[item]

    @staticmethod
    def __not__(other: Any) -> Any:
        match other:
            case Wrapper():
                return Wrapper(not other.value, other.ev.__not__())
            case a:
                return not a

    @staticmethod
    def __land__(l: Any, r: Any) -> Any:
        match (l, r):
            case (Wrapper(), Wrapper()):
                return Wrapper(l.value and r.value, l.ev.join(r.ev) if not l.value else r.ev.join(l.ev))
            case _:
                raise Exception(f"Unsupported operation: {l} and {r}")

    @staticmethod
    def __lor__(l: Any, r: Any) -> Any:
        match (l, r):
            case (Wrapper(), Wrapper()):
                return Wrapper(l.value or r.value, l.ev.join(r.ev) if l.value else r.ev.join(l.ev))
            case _:
                raise Exception(f"Unsupported operation: {l} or {r}")

    @staticmethod
    def unwrap(x: Any) -> tuple[Evidence | None, Any]:
        match x:
            case Wrapper():
                return x.ev, x.value
            case a:
                return None, a

    @staticmethod
    def unwrap_value(x: Any) -> Any:
        match x:
            case Wrapper():
                return x.value
            case a:
                return a

    @staticmethod
    def unwrap_ev(x: Any) -> Evidence | None:
        match x:
            case Wrapper():
                return x.ev
            case _:
                return None

    def __iter__(self):
        match self.ev.l.__qualname__:
            case tuple.__qualname__:
                return iter([Wrapper(v, ev) for v, ev in zip(self.value, self.ev.ituple(self.ev))])
            case list.__qualname__:
                inner_ev = self.ev.ilist(self.ev)
                return iter([Wrapper(v, inner_ev) for v in self.value])
            case a:
                raise Exception(f"Cannot unwrap a non-tuple: {a}")

    @staticmethod
    def __get_attr__(x: Any, name):
        match x:
            case Wrapper():
                # TODO: do something with the evidence of the resulting value
                return getattr(x.value, name)
            case _:
                return getattr(x, name)

    def __getitem__(self, sl):
        return self.value[sl]

    def __setitem__(self, sl, value):
        self.value[sl] = value

    def __hash__(self):
        return hash(self.value)


if __name__ == "__main__":
    pass
