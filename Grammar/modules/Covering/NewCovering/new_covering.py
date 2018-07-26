import heapq
import random
from typing import List, Set, Iterable, Dict, Tuple

from modules.Covering.SmartCovering.aggressive_smart_covering import RouletteSelection
from settings.settings import Settings
from ..Covering import Covering
from ...Crowding.crowding import Crowding
from ...GCSBase.domain.Rule import Rule
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils


class NewCovering(Covering):

    def __init__(self, crowding: Crowding, settings: Settings):
        super().__init__(crowding)
        self.roulette_selection = RouletteSelection()
        self.roulette_selection_enabled = settings.get_value('new_covering', 'roulette_selection_enabled') == "True"
        self.usage_probability = float(settings.get_value('new_covering', 'usage_probability'))
        self.the_best_rules_number = int(settings.get_value('new_covering', 'the_best_rules_number'))


    def get_left_symbol(self, grammar: Grammar) -> Symbol:
        if RandomUtils.make_random_decision_with_probability(self.usage_probability):
            return self.find_left_symbol(grammar)
        else:
            return RandomUtils.get_random_nonterminal_symbol_from(grammar)

    def find_left_symbol(self, grammar: Grammar) -> Symbol:
        the_best_rules = self.find_the_best_rules(grammar)
        if self.roulette_selection_enabled:
            return self.find_symbol_by_roulette_selection(the_best_rules)
        else:
            symbols: Set[Symbol] = self.get_right_side_symbols(the_best_rules)
            return self.pick_symbol_randomly(symbols)

    def find_the_best_rules(self, grammar: Grammar) -> List[Rule]:
        rules = grammar.get_non_terminal_rules()
        return heapq.nlargest(self.the_best_rules_number, rules, key=lambda rule: rule.fitness)

    def get_right_side_symbols(self, the_best_rules: Iterable[Rule]) -> Set[Rule]:
        symbols = set()
        for rule in the_best_rules:
            symbols.add(rule.right1)
            rule.right2 and symbols.add(rule.right2)
        return symbols

    def pick_symbol_randomly(self, symbol: Iterable[Symbol]) -> Symbol:
        return random.sample(symbol, 1)[0]

    def find_symbol_by_roulette_selection(self, the_best_rules: Iterable[Rule]) -> Symbol:
        statistics = self.count_symbols_statistics(the_best_rules)
        return self.roulette_selection.select(statistics)

    def count_symbols_statistics(self, rules: Iterable[Rule]) -> List[Tuple[Symbol, int]]:
        symbols_statistics = {}
        for rule in rules:
            self.increment_statistic_for(rule.right1, symbols_statistics)
            rule.right2 and self.increment_statistic_for(rule.right2, symbols_statistics)
        return list(symbols_statistics.items())

    def increment_statistic_for(self, symbol: Symbol, statistics: Dict[Symbol, int]) -> None:
        if symbol not in statistics:
            statistics[symbol] = 0
        statistics[symbol] += 1
