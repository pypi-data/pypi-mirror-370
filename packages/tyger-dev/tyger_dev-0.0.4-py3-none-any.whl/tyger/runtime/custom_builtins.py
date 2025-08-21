from .wrapper import Wrapper
from tyger.discipline.simple.evidence import simple_factory


class Range(object):
    ev_fact = simple_factory

    def __init__(self, start, stop=None, step=1):
        if stop is None:
            ev, v = Wrapper.unwrap(start)
            self.start = 0 if not ev else Wrapper(0, ev, self.ev_fact)
            self.stop = start
        else:
            self.start = start
            self.stop = stop
        self.step = step

        self.ev = self.ev_fact.joins(
            [Wrapper.unwrap_ev(self.start), Wrapper.unwrap_ev(self.stop), Wrapper.unwrap_ev(self.step)])

        self.start = Wrapper.unwrap_value(self.start)
        self.stop = Wrapper.unwrap_value(self.stop)
        self.step = Wrapper.unwrap_value(self.step)

        self.current = self.start

    def __iter__(self):
        return self

    def __next__(self):
        b = self.step > 0 and self.current >= self.stop or self.step < 0 and self.current <= self.stop
        if b:
            raise StopIteration
        else:
            current = self.current
            self.current += self.step
            return current if not self.ev else Wrapper.join(
                Wrapper(current, simple_factory.get_evidence(int, int), self.ev_fact), self.ev)
