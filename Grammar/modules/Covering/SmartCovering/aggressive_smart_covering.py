import random
from typing import List, Tuple, Dict

from ..Covering import Covering
from ...Crowding.crowding import Crowding
from ...GCSBase.domain.Rule import Rule, RuleOrigin
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils
from ...sGCS.domain.sRule import sRuleBuilder


class AggressiveSmartCovering(Covering):

    def __init__(self, crowding: Crowding):
        super().__init__(crowding)
        self.roulette_selection = RouletteSelection()

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        new_rule = self.produce_rule(grammar, first_symbol, second_symbol)
        self.crowding.add_rule(grammar, new_rule)
        self.iteration.add_covering_rule(new_rule)
        return new_rule

    def produce_rule(self, grammar: Grammar, first_right_symbol: Symbol, second_right_symbol: Symbol) -> Rule:
        left_symbol = self.get_left_symbol(grammar)
        probability = RandomUtils.get_random_probability()
        return sRuleBuilder() \
            .left_symbol(left_symbol) \
            .first_right_symbol(first_right_symbol) \
            .second_right_symbol(second_right_symbol) \
            .probability(probability) \
            .origin(RuleOrigin.COVERING) \
            .create()

    def get_left_symbol(self, grammar: Grammar) -> Symbol:
        if RandomUtils.make_random_decision_with_probability(0.6):
            return self.find_left_symbol_wisely(grammar)
        else:
            return RandomUtils.get_random_nonterminal_symbol_from(grammar)

    def find_left_symbol_wisely(self, grammar: Grammar) -> Symbol:
        symbols_statistics = self.count_symbols_statistics(grammar)

        if len(symbols_statistics) == 0:
            return RandomUtils.get_random_nonterminal_symbol_from(grammar)

        the_best_symbols_statistics = self.find_the_best_symbols(symbols_statistics, number_of_symbols=8)
        return self.roulette_selection.select(the_best_symbols_statistics)

    def find_the_best_symbols(self, statistics: Dict[Symbol, int], number_of_symbols: int) -> List[Tuple[Symbol, int]]:
        sorted_symbols = sorted(statistics.items(), key=lambda x: x[1], reverse=True)
        return sorted_symbols[:number_of_symbols]

    def count_symbols_statistics(self, grammar: Grammar) -> Dict[Symbol, int]:
        symbols_statistics = {}
        for rule in grammar.get_rules():
            first_right_symbol = rule.right1
            second_right_symbol = rule.right2

            if first_right_symbol.is_non_terminal():
                self.increment_statistic_for(first_right_symbol, symbols_statistics)

            if second_right_symbol is not None and second_right_symbol.is_non_terminal():
                self.increment_statistic_for(second_right_symbol, symbols_statistics)
        return symbols_statistics

    def increment_statistic_for(self, symbol: Symbol, statistics: Dict[Symbol, int]) -> None:
        if symbol not in statistics:
            statistics[symbol] = 0
        statistics[symbol] += 1


class RouletteSelection:

    def select(self, symbol_statistics: List[Tuple[Symbol, int]]) -> Symbol:
        roulette_wheel_size = self.sum_values(symbol_statistics)
        wheel_sections = self.count_sections_of_roulette_wheel(symbol_statistics)
        point_on_wheel = random.randint(0, roulette_wheel_size)
        return self.find_symbol(symbol_statistics, wheel_sections, point_on_wheel)

    def sum_values(self, symbol_statistics: List[Tuple]):
        return sum(x[1] for x in symbol_statistics)

    def count_sections_of_roulette_wheel(self, symbol_statistics: List[Tuple[Symbol, int]]) -> List[int]:
        size = len(symbol_statistics)
        wheel_ranges = [0] * size
        wheel_ranges[-1] = symbol_statistics[-1][1]
        for i in reversed(range(size - 1)):
            wheel_ranges[i] += symbol_statistics[i][1] + wheel_ranges[i + 1]
        return wheel_ranges

    def find_symbol(self, symbol_statistics: List[Tuple[Symbol, int]], wheel_sections: List[int],
                    point_on_wheel: int) -> Symbol:
        left_symbol = symbol_statistics[-1][0]
        for i in range(len(symbol_statistics)):
            if wheel_sections[i] >= point_on_wheel:
                left_symbol = symbol_statistics[i][0]
        return left_symbol
