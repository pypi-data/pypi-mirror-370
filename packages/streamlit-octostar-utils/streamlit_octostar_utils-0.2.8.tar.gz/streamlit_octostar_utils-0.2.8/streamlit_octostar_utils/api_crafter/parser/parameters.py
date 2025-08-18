from .generics import Parameters


class ConsolidationParameters(Parameters):
    def __init__(
        self, equality_tolerances=dict(), similarity_tolerances=dict(), keep_roots=True
    ):
        super().__init__()
        self.equality_tolerances = equality_tolerances
        self.similarity_tolerances = similarity_tolerances
        self.keep_roots = keep_roots


class GroupbyParameters(Parameters):
    def __init__(self, groups=dict()):
        super().__init__()
        self.groups = groups
