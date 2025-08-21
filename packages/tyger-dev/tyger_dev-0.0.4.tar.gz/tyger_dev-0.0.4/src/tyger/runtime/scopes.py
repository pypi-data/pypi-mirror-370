from typing import Any

from tyger.runtime.contextual_information import thlci
from tyger.runtime.wrapper import Wrapper


class ConditionalScope:

    ev = None

    def __init__(self, v: Any):
        self.ev, self.value = Wrapper.unwrap(v)
        if self.ev:
            thlci.push(self.ev)

    def __enter__(self):
        # print("Entering conditional scope")
        return self.value

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ev:
            thlci.pop()
        return False


class ComprehensionHelper:
    ev = None

    @staticmethod
    def for_check(f: Any):
        ev, value = Wrapper.unwrap(f)
        thlci.push(ev)
        return value

    @staticmethod
    def for_yield(v: Any):
        ev = None
        if len(thlci.evs) > 0:
            ev = thlci.pop()

        return Wrapper.join(v, ev) if ev else v


class LoopScope:
    ev = None

    def __init__(self):
        self.ev = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.ev:
            thlci.pop()
        return False

    def extract(self, value: Any):
        ev, raw_value = Wrapper.unwrap(value)
        if ev:
            if not self.ev:
                self.ev = ev
            else:
                self.ev = self.ev.join(ev)
                thlci.pop()
            thlci.push(self.ev)
        return raw_value
