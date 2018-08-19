from ..domain import Coordinates
from ..domain.Rule import Rule


class CellRule:
    def __init__(self, rule: Rule = None, c1: Coordinates = None, c2: Coordinates = None):
        self.rule = rule
        self.cell_2_coordinates: Coordinates = c2
        self.cell_1_coordinates: Coordinates = c1
        self.root_cell_coordinates = None
        self.used_in_parsing = False
        self.called_number = 0
        self.tmp_val = 0.0
        self.parsed = False
        self.index = None
        self.proceeded = False

    def __eq__(self, other):
        if type(self) is type(other):
            return self.rule == other.rule
        return False

    def __hash__(self) -> int:
        return hash(self.rule)
