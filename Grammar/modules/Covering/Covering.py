import logging

from modules.Crowding.crowding import Crowding
from modules.Visualisation.iteration import Iteration
from ..GCSBase.domain import Rule
from ..GCSBase.domain.symbol import Symbol
from ..GCSBase.grammar.grammar import Grammar


class Covering:

    def __init__(self, crowding: Crowding = None):
        self.crowding = crowding
        self.iteration: Iteration = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        raise NotImplementedError

    def set_iteration(self, iteration: Iteration) -> None:
        self.iteration = iteration

    def log_rule(self, new_rule: Rule, was_added: bool = True):
        if was_added:
            self.logger.info("{0} - rule: {1} was added".format(self.__class__.__name__, new_rule))
        else:
            self.logger.info("{0} - rule: {1} was rejected".format(self.__class__.__name__, new_rule))
