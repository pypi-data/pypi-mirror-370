from abc import ABC, abstractmethod


class Evidence(ABC):
    l: type
    r: type

    @abstractmethod
    def is_tuple(self) -> bool: ...

    @abstractmethod
    def is_list(self) -> bool: ...

    @abstractmethod
    def is_dict(self) -> bool: ...

    @abstractmethod
    def trans(self, other: "Evidence") -> "Evidence": ...

    @abstractmethod
    def idomcod(self) -> tuple: ...

    @staticmethod
    @abstractmethod
    def ituple(ev: "Evidence") -> list["Evidence"]: ...

    @staticmethod
    @abstractmethod
    def ilist(ev: "Evidence") -> list["Evidence"]: ...

    @staticmethod
    @abstractmethod
    def custom_assign_runtime_check(*args): ...

    @staticmethod
    @abstractmethod
    def interior(t1, t2) -> "Evidence": ...

    @abstractmethod
    def join(self, other: "Evidence") -> "Evidence": ...

    @abstractmethod
    def __neg__(self) -> "Evidence": ...

    @staticmethod
    @abstractmethod
    def idict(ev: "Evidence") -> tuple["Evidence", "Evidence"]: ...


class EvidenceFactory(ABC):
    @abstractmethod
    def interior(self, l: type, r: type) -> Evidence:
        ...

    @abstractmethod
    def each_interior(self, l, r) -> tuple | Evidence:
        ...

    @abstractmethod
    def get_evidence(self, l, r) -> Evidence: ...

    @abstractmethod
    def ituple(self, ev: Evidence) -> list[Evidence]: ...

    @abstractmethod
    def ilist(self, ev: Evidence) -> Evidence: ...

    @abstractmethod
    def idict(self, ev: Evidence) -> tuple[Evidence, Evidence]: ...

    @abstractmethod
    def custom_assign_runtime_check(self, value, ev, ev_pc, *args): ...

    @abstractmethod
    def joins(self, evs: list[Evidence]) -> Evidence: ...
