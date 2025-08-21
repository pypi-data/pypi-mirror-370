from typing import Callable, get_args

from tyger.discipline.base.evidence import BaseEvidenceFactory, RuntimeException
from tyger.discipline.evidence import Evidence
from tyger.discipline.simple.types import unk
from functools import reduce


class etype(type):
    pass


class SimpleEvidenceFactory(BaseEvidenceFactory):

    def get_evidence(self, l, r) -> "SimpleEvidence":
        return SimpleEvidence(l, r)

    def interior(self, from_type: type, to_type: type) -> "SimpleEvidence":
        # print(f"interior between {l} and {r}")
        match (from_type.__qualname__, to_type.__qualname__):
            case ("NoneType", "NoneType") | ("NoneType", unk.__qualname__) | (unk.__qualname__, "NoneType"):
                return SimpleEvidence(unk, unk)
            case (unk.__qualname__, _) | ("NoneType", _):
                return SimpleEvidence(to_type, to_type)
            case (_, unk.__qualname__) | (_, "NoneType"):
                return SimpleEvidence(from_type, from_type)
            case (Callable.__qualname__, Callable.__qualname__):
                dom1, cod1 = get_args(from_type)
                dom2, cod2 = get_args(to_type)

                if len(dom1) > len(dom2):
                    dom2.extend([unk] * (len(dom1) - len(dom2)))
                elif len(dom2) > len(dom1):
                    dom1.extend([unk] * (len(dom2) - len(dom1)))
                # print(dom1, dom2)
                edom = reduce(lambda x, y: x + y, map(lambda p: [self.interior(p[0], p[1])], zip(dom2, dom1))) if len(
                    dom1) > 0 else []
                ecod = self.interior(cod1, cod2)
                # edom = [<r1,l1>, <r2,l2>, ...]
                # ecod = <lk, rk>
                # ev = <Callable[[l1,l2,...], lk], Callable[[r1,r2,...], rk]>
                ldom = map(lambda e: e.r, edom)
                rdom = map(lambda e: e.l, edom)
                return SimpleEvidence(Callable[[*ldom], ecod.l], Callable[[*rdom], ecod.r])
            case (tuple.__qualname__, tuple.__qualname__):
                largs = get_args(from_type)
                rargs = get_args(to_type)
                if len(largs) != len(rargs):
                    raise Exception(f"Tuple length mismatch: {len(largs)} != {len(rargs)}")
                interiors = [self.interior(l, r) for l, r in zip(largs, rargs)]
                return SimpleEvidence(tuple[*[i.l for i in interiors]], tuple[*[i.r for i in interiors]])
            case (list.__qualname__, list.__qualname__):

                left_ty = get_args(from_type)[0] if len(get_args(from_type)) > 0 else unk
                right_ty = get_args(to_type)[0] if len(get_args(to_type)) > 0 else unk
                i = self.interior(left_ty, right_ty)
                return SimpleEvidence(list[i.l], list[i.r])

            case dict.__qualname__, dict.__qualname__:
                left_dom, left_cod = get_args(from_type)
                right_dom, right_cod = get_args(to_type)
                dom_ev = self.interior(left_dom, right_dom)
                cod_ev = self.interior(left_cod, right_cod)
                return SimpleEvidence(dict[dom_ev.l, cod_ev.l], dict[dom_ev.r, cod_ev.r])

            case (a, b):
                if a == b:
                    return SimpleEvidence(from_type, to_type)
                else:
                    raise Exception(f"Interior Type mismatch: {a} != {b}")
        return SimpleEvidence(from_type, to_type)

simple_factory = SimpleEvidenceFactory()


class SimpleEvidence(Evidence):

    def is_dict(self) -> bool:
        dict_qualname = dict.__qualname__
        return self.l.__qualname__ == dict_qualname and self.r.__qualname__ == dict_qualname

    @staticmethod
    def idict(ev: "Evidence") -> tuple["Evidence", "Evidence"]:
        return simple_factory.idict(ev)

    @staticmethod
    def ituple(ev: "SimpleEvidence") -> list["SimpleEvidence"]:
        return simple_factory.ituple(ev)

    @staticmethod
    def ilist(ev: "Evidence") -> list["Evidence"]:
        return simple_factory.ilist(ev)

    @staticmethod
    def custom_assign_runtime_check(*args):
        return simple_factory.custom_assign_runtime_check(*args)

    @staticmethod
    def interior(t1, t2) -> "Evidence":
        return simple_factory.interior(t1, t2)

    def __init__(self, l: type, r: type):
        self.l = l
        self.r = r

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<{self.l.__qualname__}, {self.r.__qualname__}>"

    def is_tuple(self):
        return self.l.__qualname__ == tuple.__qualname__ and self.r.__qualname__ == tuple.__qualname__

    def is_list(self):
        return self.l.__qualname__ == list.__qualname__ and self.r.__qualname__ == list.__qualname__

    def __add__(self, other):
        # TODO: tailor to the specific operation
        return self

    def __sub__(self, other):
        # TODO: tailor to the specific operation
        return self

    def __mul__(self, other):
        # TODO: tailor to the specific operation
        return self

    def __lt__(self, other):
        # TODO: tailor to the specific operation
        return SimpleEvidence(bool, bool)

    def __le__(self, other):
        # TODO: tailor to the specific operation
        return SimpleEvidence(bool, bool)

    def __gt__(self, other):
        # TODO: tailor to the specific operation
        return SimpleEvidence(bool, bool)

    def __ge__(self, other):
        # TODO: tailor to the specific operation
        return SimpleEvidence(bool, bool)

    def eq(self, other):
        # TODO: tailor to the specific operation
        return SimpleEvidence(bool, bool)

    def __ne__(self, other):
        # TODO: tailor to the specific operation
        return SimpleEvidence(bool, bool)

    def __neg__(self):
        # TODO: tailor to the specific operation
        return self

    def __mod__(self, other):
        # TODO: tailor to the specific operation
        return self

    def __land__(self, other):
        return self

    def __lor__(self, other):
        return self

    def __not__(self):
        return SimpleEvidence(bool, bool)

    def trans(self, r: 'SimpleEvidence') -> 'SimpleEvidence':
        try:
            m: type = self.meet(self.r, r.l)
            return SimpleEvidence(self.interior(self.l, m).l, self.interior(r.r, m).r)
        except Exception as e:
            raise RuntimeException(f"Transitivity error: {e}")

    def join(self, r: 'SimpleEvidence') -> 'SimpleEvidence':
        # for now is just the left evidence
        return self

    def idomcod(self) -> tuple[list['SimpleEvidence'], 'SimpleEvidence']:
        match (self.l.__qualname__, self.r.__qualname__):
            case (Callable.__qualname__, Callable.__qualname__):
                dom1, cod1 = get_args(self.l)
                dom2, cod2 = get_args(self.r)
                return [SimpleEvidence(l, r) for (l, r) in zip(dom2, dom1)], SimpleEvidence(cod1, cod2)
            case _:
                raise Exception(f"Cannot get domain of {self}")

    def meet(self, l: type, r: type) -> type:
        # match (l.__qualname__,r.__qualname__):
        #    case (unk.__qualname__, _):
        return self.interior(l, r).l

def custom_assign_runtime_check(*args):
    pass

