import functools
from abc import ABC
from typing import get_args

from tyger.discipline.evidence import EvidenceFactory, Evidence
from tyger.discipline.base.types import unk


class RuntimeException(Exception):
    pass


class BaseEvidenceFactory(EvidenceFactory, ABC):
    def each_interior(self, from_type, to_type):
        # Right types
        match from_type.__qualname__:
            case unk.__qualname__:
                # Check if we are handling a tuple or
                match to_type:
                    case tuple():
                        tys = tuple(unk for _ in range(len(to_type)))
                    case _:
                        tys = None
            case tuple.__qualname__:
                tys = get_args(from_type)
            case list.__qualname__:
                tys = get_args(from_type) * len(to_type)
            case _:
                tys = None
        # Now get each interior
        match to_type:
            case tuple():
                return tuple(self.each_interior(_l, _r) for _l, _r in zip(tys, to_type))
            case type():  # TODO: maybe it is not necessary to cast on None case
                return self.interior(from_type, to_type)

    def ilist(self, ev: Evidence) -> Evidence:
        match (ev.l.__qualname__, ev.r.__qualname__):
            case (list.__qualname__, list.__qualname__):
                return self.get_evidence(get_args(ev.l)[0], get_args(ev.r)[0])
            case _:
                raise Exception(f"Cannot get list of {ev}")

    def ituple(self, ev: Evidence) -> list[Evidence]:
        match (ev.l.__qualname__, ev.r.__qualname__):
            case (tuple.__qualname__, tuple.__qualname__):
                return [self.get_evidence(l, r) for (l, r) in zip(get_args(ev.l), get_args(ev.r))]
            case _:
                raise Exception(f"Cannot get tuple of {ev}")

    def idict(self, ev: Evidence) -> tuple[Evidence, Evidence]:
        match ev.l.__qualname__, ev.r.__qualname__:
            case dict.__qualname__, dict.__qualname__:
                left_dom, left_cod = get_args(ev.l)
                right_dom, right_cod = get_args(ev.r)
                return self.get_evidence(left_dom, right_dom), self.get_evidence(left_cod, right_cod)
    def custom_assign_runtime_check(self, value, ev, ev_pc, *args):
        pass

    def joins(self, evs: list[Evidence]) -> Evidence:
        return functools.reduce(lambda x, y: x.join(y) if x and y else (x or y), evs)
