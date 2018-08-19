import logging
import _pickle as pickle
from collections import Set

from modules.Crowding.crowding import Crowding
from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.grammar.grammar import Grammar
from modules.Visualisation.iteration import Iteration
from modules.Visualisation.report_rule import ReportRule


class Heuristic:

    def __init__(self, crowding: Crowding = None, settings=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.crowding = crowding
        self.settings = settings
        self.iteration: Iteration = Iteration()
        self.first_report_rule: ReportRule = None
        self.second_report_rule: ReportRule = None
        self.__last_grammar_fitness: float = -1.0
        self.__last_rules: Set[Rule] = None

    def run(self, grammar: Grammar) -> None:
        raise NotImplementedError

    def set_iteration(self, iteration: Iteration) -> None:
        self.iteration = iteration

    def reset(self):
        self.__last_grammar_fitness = -1.0

    def save_grammar_state(self, grammar: Grammar) -> None:
        self.__last_rules = pickle.loads(pickle.dumps(grammar.get_rules(), -1))
        self.__last_grammar_fitness = self.__count_grammar_fitness(grammar)

    def __count_grammar_fitness(self, grammar: Grammar) -> float:
        number_of_rules: int = grammar.truePositive + grammar.trueNegative + grammar.falsePositive + grammar.falseNegative
        return grammar.calculate_grammar_fitness(number_of_rules)

    def restore_if_necessary(self, grammar: Grammar) -> None:
        if self.__grammar_is_worse_than_previously(grammar):
            print("[heuristic] restoring grammar")
            self.__restore_previous_state(grammar)
        else:
            print('[heuristic] Oh yeah! The grammar is better')

    def __grammar_is_worse_than_previously(self, grammar: Grammar) -> bool:
        print("[heuristic] grammar fitness = {}".format(self.__count_grammar_fitness(grammar)))
        print("[heuristic] last grammar fitness = {}".format(self.__last_grammar_fitness))
        if len(grammar.get_rules()) > 5 * int(
                    self.settings.get_value('general', 'non_terminal_productions_number')):
            return True
        return self.__count_grammar_fitness(grammar) < self.__last_grammar_fitness

    def __restore_previous_state(self, grammar: Grammar) -> None:
        to_remove = set(grammar.get_rules())
        for rule in to_remove:
            grammar.remove_rule(rule)
            self.iteration.remove_crowding_rule(rule)
        for rule in self.__last_rules:
            grammar.add_rule(rule)
            self.iteration.add_rule(rule)
