import logging
from typing import List

from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.grammar.grammar import Grammar
from modules.Visualisation.iteration import Iteration


class Crowding:
    def __init__(self, settings=None):
        self.settings = settings
        self.iteration: Iteration = Iteration()
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_rule(self, grammar: Grammar, rule: Rule) -> bool:
        raise NotImplementedError

    def add_rules(self, grammar: Grammar, rules: List[Rule]) -> None:
        raise NotImplementedError

    def set_iteration(self, iteration: Iteration) -> None:
        self.iteration = iteration
