import ast
from functools import reduce
from typing import get_args, Callable

from ..base.evidence import BaseEvidenceFactory
from ..base.types import unk
from ..evidence import Evidence

from .types import static_join, static_meet, leq, Bot, Top, extract_cod_lbl_lat, CodType, extract_lbl


class RuntimeException(Exception):
    pass


"""
i := [l, l]
T := unk | bool | int | E -i-> E 
E := T i
"""


class interval(object):
    def __init__(self, l: type, r: type):
        self.l = l
        self.r = r

    def __str__(self):
        return f"[{self.l.__qualname__}, {self.r.__qualname__}]"

    def __repr__(self):
        return self.__str__()

    def meet(self, other: 'interval') -> 'interval':
        ml = static_join(self.l, other.l)
        mr = static_meet(self.r, other.r)
        if leq(ml, mr):
            return interval(ml, mr)
        else:
            raise RuntimeException(f"Meet error: {self} and {other}")

    def join(self, other: 'interval') -> 'interval':
        ml = static_join(self.l, other.l)
        mr = static_join(self.r, other.r)
        return interval(ml, mr)


class E(object):
    def __init__(self, ty: 'T', i: interval):
        self.ty = ty
        self.i = i

    def meet(self, other: 'E') -> 'E':
        return E(self.ty.meet(other.ty), self.i.meet(other.i))

    def __str__(self):
        return f"{self.ty}_{self.i}"

    def __repr__(self):
        return self.__str__()

    def ilbl(self) -> interval:
        return self.i

    def ilat(self) -> interval:
        return self.ty.ilat()

    def dom(self) -> list['E']:
        match self.ty:
            case TCallable():
                return self.ty.dom
            case _:
                raise Exception(f"Cannot get domain of {self}")

    def cod(self) -> 'E':
        match self.ty:
            case TCallable():
                return self.ty.cod.join(self.i)
            case _:
                raise Exception(f"Cannot get codomain of {self}")

    def join(self, other: interval) -> 'E':
        return E(self.ty, self.i.join(other))


class T:
    def meet(self, other: 'T') -> 'T':
        match (self, other):
            case (TUnk(), _):
                return other
            case (_, TUnk()):
                return self
            case (TCallable(), TCallable()):
                d = [d2.meet(d1) for d1, d2 in zip(self.dom, other.dom)]
                c = self.cod.meet(other.cod)
                lat = other.lat.meet(self.lat)
                return TCallable(d, c, lat)
            case _:
                if self == other:
                    return self
                else:
                    raise RuntimeException(f"Meet error: {self} and {other}")

    def __str__(self):
        pass

    def ilat(self):
        raise Exception(f"Cannot get lat of {self}")


class TUnk(T):
    def __str__(self):
        return "unk"


class TBool(T):
    def __str__(self):
        return "bool"


class TInt(T):
    def __str__(self):
        return "int"


class TCallable(T):
    def __init__(self, dom: list[E], cod: E, lat: interval):
        self.dom = dom
        self.cod = cod
        self.lat = lat

    def __str__(self):
        return f"({self.dom} -{self.lat}> {self.cod})"

    def ilat(self):
        return self.lat


def ituple(ev: "SecurityEvidence") -> list["SecurityEvidence"]:
    match (ev.l.__qualname__, ev.r.__qualname__):
        case (tuple.__qualname__, tuple.__qualname__):
            return [SecurityEvidence(l, r) for (l, r) in zip(get_args(ev.l), get_args(ev.r))]
        case _:
            raise Exception(f"Cannot get tuple of {ev}")


def ilist(ev: "SecurityEvidence") -> "SecurityEvidence":
    match (ev.l.__qualname__, ev.r.__qualname__):
        case (list.__qualname__, list.__qualname__):
            return SecurityEvidence(get_args(ev.l)[0], get_args(ev.r)[0])
        case _:
            raise Exception(f"Cannot get list of {ev}")


def interior_interval(l: type, r: type) -> tuple[interval, interval]:
    match (l.__qualname__, r.__qualname__):
        case (unk.__qualname__, unk.__qualname__) | ("NoneType", "NoneType"):
            return interval(Bot, Top), interval(Bot, Top)
        case (unk.__qualname__, _) | ("NoneType", _):
            return interval(Bot, r), interval(r, r)
        case (_, unk.__qualname__) | (_, "NoneType"):
            return interval(l, l), interval(l, Top)
        case (a, b):
            if issubclass(l, r):
                return interval(l, l), interval(r, r)
            else:
                raise Exception(f"Interior Type mismatch: {a} != {b}")


class SecurityEvidenceFactory(BaseEvidenceFactory):
    def interior(self, l: type, r: type) -> "SecurityEvidence":
        match (l.__qualname__, r.__qualname__):
            case (unk.__qualname__, unk.__qualname__) | ("NoneType", "NoneType"):
                li, ri = interior_interval(unk, unk)
                return SecurityEvidence(E(TUnk(), li), E(TUnk(), ri))

            case (Callable.__qualname__, Callable.__qualname__):
                dom1, cod1 = get_args(l)
                dom2, cod2 = get_args(r)

                edom = reduce(lambda x, y: x + y, map(lambda p: [self.interior(p[0], p[1])], zip(dom2, dom1))) if len(
                    dom1) > 0 else []
                cod1, lbl1, lat1 = extract_cod_lbl_lat(cod1)
                cod2, lbl2, lat2 = extract_cod_lbl_lat(cod2)

                ecod = self.interior(cod1, cod2)
                lbl1, lbl2 = interior_interval(lbl1, lbl2)
                lat2, lat1 = interior_interval(lat2, lat1)

                dom1 = map(lambda e: e.r, edom)
                dom2 = map(lambda e: e.l, edom)
                return SecurityEvidence(E(TCallable(dom1, ecod.l, lat1), lbl1), E(TCallable(dom2, ecod.r, lat2), lbl2))
            case (unk.__qualname__, Callable.__qualname__):
                dom, _ = get_args(r)
                return self.interior(Callable[[*((unk,) * len(dom))], CodType[unk, unk, unk]], r)
            case (Callable.__qualname__, unk.__qualname__):
                dom, _ = get_args(l)
                return self.interior(l, Callable[[*((unk,) * len(dom))], CodType[unk, unk, unk]])
            #TODO:
            case (tuple.__qualname__, tuple.__qualname__):
                largs = get_args(l)
                rargs = get_args(r)
                if len(largs) != len(rargs):
                    raise Exception(f"Tuple length mismatch: {len(largs)} != {len(rargs)}")
                interiors = [self.interior(l, r) for l, r in zip(largs, rargs)]
                return SecurityEvidence(tuple[*[i.l for i in interiors]], tuple[*[i.r for i in interiors]])
            #TODO:
            case (list.__qualname__, list.__qualname__):

                left_ty = get_args(l)[0] if len(get_args(l)) > 0 else unk
                right_ty = get_args(r)[0] if len(get_args(r)) > 0 else unk
                i = self.interior(left_ty, right_ty)
                return SecurityEvidence(list[i.l], list[i.r])

            case (unk.__qualname__, _) | ("NoneType", _):
                return SecurityEvidence(E(TUnk(), interval(Bot, r)), E(TUnk(), interval(r, r)))
            case (_, unk.__qualname__) | (_, "NoneType"):
                return SecurityEvidence(E(TUnk(), interval(l, l)), E(TUnk(), interval(l, Top)))

            case (a, b):
                if issubclass(l, r):
                    return SecurityEvidence(E(TUnk(), interval(l, l)), E(TUnk(), interval(r, r)))
                else:
                    raise Exception(f"Interior Type mismatch: {a} != {b}")

    def get_evidence(self, l, r) -> "SecurityEvidence":
        return SecurityEvidence(l, r)

    def custom_assign_runtime_check(self, value, ev, ev_pc, *args):
        ev_assign, stored_value = args
        if stored_value and not leq(ev_assign.r.i.l, stored_value.ev.r.i.l):
            raise RuntimeException(f"NSU check fails between {ev_assign.r.i.l} and  {stored_value.ev.r.i.l}")

    @staticmethod
    def ev_fact_to_ast():
        return ast.Name("security_factory", ast.Load())


security_factory = SecurityEvidenceFactory()


class SecurityEvidence(Evidence):
    @staticmethod
    def ituple(ev: "Evidence") -> list["Evidence"]:
        return security_factory.ituple(ev)

    @staticmethod
    def ilist(ev: "Evidence") -> list["Evidence"]:
        return security_factory.ilist(ev)

    @staticmethod
    def custom_assign_runtime_check(*args):
        return security_factory.custom_assign_runtime_check(*args)

    @staticmethod
    def interior(t1, t2) -> "Evidence":
        return security_factory.interior(t1, t2)

    def __init__(self, l: E, r: E):
        self.l = l
        self.r = r

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<{self.l}, {self.r}>"

    def ilbl(self) -> interval:
        return SecurityEvidence(E(TUnk(), self.l.ilbl()), E(TUnk(), self.r.ilbl()))

    def ilat(self) -> interval:
        return SecurityEvidence(E(TUnk(), self.l.ilat()), E(TUnk(), self.r.ilat()))

    def is_tuple(self):
        return False
        return self.l.l.__qualname__ == tuple.__qualname__ and self.r.l.__qualname__ == tuple.__qualname__

    def is_list(self):
        return False
        return self.l.l.__qualname__ == list.__qualname__ and self.r.l.__qualname__ == list.__qualname__

    def taint(self, other: 'SecurityEvidence') -> 'SecurityEvidence':
        return SecurityEvidence(self.l.join(other.l.i), self.r.join(other.r.i))

    def __add__(self, other):
        return self.taint(other)

    def __sub__(self, other):
        return self.taint(other)

    def __mul__(self, other):
        return self.taint(other)

    def __lt__(self, other):
        return self.taint(other)

    def __le__(self, other):
        return self.taint(other)

    def __gt__(self, other):
        return self.taint(other)

    def __ge__(self, other):
        return self.taint(other)

    def eq(self, other):
        return self.taint(other)

    def __ne__(self, other):
        return self.taint(other)

    def __neg__(self):
        return self

    def __land__(self, other):
        return self.taint(other)

    def __lor__(self, other):
        return self.taint(other)

    def __not__(self):
        return SecurityEvidence(interval(extract_lbl(self.l.l), extract_lbl(self.l.r)),
                                interval(extract_lbl(self.r.l), extract_lbl(self.r.r)))

    def trans(self, r: 'SecurityEvidence') -> 'SecurityEvidence':
        try:
            print(f"computing trans between {self} and {r}")
            m: E = self.r.meet(r.l)
            E1, _ = interior_E(self.l, m)
            _, E2 = interior_E(m, r.r)
            return SecurityEvidence(E1, E2)
        except Exception as e:
            raise RuntimeException(f"Transitivity error: {e}")

    def join(self, r: 'SecurityEvidence', extra_ev: 'SecurityEvidence' = None, *args) -> 'SecurityEvidence':
        print(f"caleta de weas: {self} \/ {r} o {extra_ev}")
        if extra_ev:
            r = r.trans(extra_ev)
        return self.taint(r)

    def idomcod(self) -> tuple[list['SecurityEvidence'], 'SecurityEvidence']:
        match (self.l.ty, self.r.ty):
            case (TCallable(), TCallable()):
                dom1 = self.l.dom()
                dom2 = self.r.dom()
                cod1 = self.l.cod()
                cod2 = self.r.cod()
                return [SecurityEvidence(l, r) for (l, r) in zip(dom2, dom1)], SecurityEvidence(cod1, cod2)

            case _:
                raise Exception(f"Cannot get domain of {self}")


def interior_E(l: E, r: E) -> tuple[E, E]:
    T1, T2 = interior_T(l.ty, r.ty)
    i1, i2 = interior_i(l.i, r.i)
    return E(T1, i1), E(T2, i2)


def interval_bounds(ty: type) -> interval:
    match ty.__qualname__:
        case unk.__qualname__:
            return interval(Bot, Top)
        case _:
            return interval(ty, ty)


def interior_i(l: interval, r: interval) -> tuple[interval, interval]:
    if leq(l.l, static_meet(l.r, r.r)) and leq(static_join(l.l, r.l), r.r):
        return interval(l.l, static_meet(l.r, r.r)), interval(static_join(l.l, r.l), r.r)
    else:
        raise RuntimeException(f"Interior error: {l} and {r}")


def interior_T(l: T, r: T) -> tuple[T, T]:
    match (l, r):
        case (TUnk(), TUnk()):
            return TUnk(), TUnk()
        case (TCallable(), TCallable()):
            doms = [interior_E(dr, dm) for dr, dm in zip(r.dom, l.dom)]
            cod1, cod2 = interior_E(l.cod, r.cod)
            lat2, lat1 = interior_i(r.lat, l.lat)
            dom1 = [d[1] for d in doms]
            dom2 = [d[0] for d in doms]
            return TCallable(dom1, cod1, lat1), TCallable(dom2, cod2, lat2)
        case (TUnk(), TCallable()):
            return TCallable([*((TUnk(),) * len(r.dom))], E(TUnk(), interval(Bot, Top)), interval(Bot, Top)), r
        case (TCallable(), TUnk()):
            return l, TCallable([*((TUnk(),) * len(l.dom))], E(TUnk(), interval(Bot, Top)), interval(Bot, Top))
        case _:
            if l == r:
                return l, r
            else:
                raise RuntimeException(f"interior error: {l} and {r}")


def joins(evs: list[Evidence]) -> Evidence:
    return reduce(lambda x, y: x.join(y) if x and y else (x or y), evs)


def custom_call(func, ev3, ev1, *argsp):
    from tyger.runtime.contextual_information import thlci
    ev = func.ev if "ev" in func.__dir__() else ev1
    # There must be an initial evidence pc
    evs = thlci.evs if len(thlci.evs) else [security_factory.interior(Bot, Bot)]

    ev_pc = reduce(lambda x, y: x.join(y), evs)
    # NSU custom check
    ev_pc.join(ev.ilbl()).trans(ev3).trans(ev.ilat())
    return func(*argsp)
