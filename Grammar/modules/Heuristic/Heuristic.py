import logging

from modules.Crowding.crowding import Crowding
from modules.GCSBase.grammar.grammar import Grammar
from modules.Visualisation.iteration import Iteration
from modules.Visualisation.report_rule import ReportRule


class Heuristic:

    def __init__(self, crowding: Crowding, settings=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.crowding = crowding
        self.settings = settings
        self.iteration: Iteration = Iteration()
        self.first_report_rule: ReportRule = None
        self.second_report_rule: ReportRule = None

    def add_new_rules(self, grammar: Grammar) -> None:
        raise NotImplementedError

    def set_iteration(self, iteration: Iteration) -> None:
        self.iteration = iteration
