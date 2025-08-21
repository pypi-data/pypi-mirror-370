from tyger.discipline.evidence import Evidence


class ContextualInformation(object):
    def __init__(self):
        self.evs: list[Evidence] = []
        self.program = ""

    def push(self, ev: Evidence):
        self.evs.append(ev)

    def pop(self) -> Evidence | None:
        return self.evs.pop() if len(self.evs) > 0 else None


# thread local contextual information for taint evidence (if/while)
thlci = ContextualInformation()
