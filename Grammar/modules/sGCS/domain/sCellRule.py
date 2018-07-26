from modules.GCSBase.domain.CellRule import CellRule
from modules.GCSBase.domain.Coordinates import Coordinates
from modules.GCSBase.domain.Rule import Rule


class sCellRule(CellRule):
    def __init__(self, rule: Rule, coordinates_x: Coordinates = None, coordinates_y: Coordinates = None):
        super().__init__(rule, coordinates_x, coordinates_y)
        self.inside = 0.0
        self.outside = 0.0
        self.calculated = False
