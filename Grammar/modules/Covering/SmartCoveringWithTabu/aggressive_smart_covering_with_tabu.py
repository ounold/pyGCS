from collections import deque

from ..SmartCovering.aggressive_smart_covering import AggressiveSmartCovering
from ...Crowding.crowding import Crowding
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils


class AggressiveSmartCoveringWithTabu(AggressiveSmartCovering):

    def __init__(self, crowding: Crowding):
        super().__init__(crowding)
        self.tabu_queue: deque[Symbol] = deque()
        self.tabu_size: int = 4

    def find_left_symbol_wisely(self, grammar: Grammar) -> Symbol:
        symbols_statistics = self.count_symbols_statistics(grammar)

        if len(symbols_statistics) == 0:
            return RandomUtils.get_random_nonterminal_symbol_from(grammar)

        self.purify_statistics_based_on_tabu(symbols_statistics)

        the_best_symbols_statistics = self.find_the_best_symbols(symbols_statistics, number_of_symbols=5)
        new_symbol: Symbol = self.roulette_selection.select(the_best_symbols_statistics)

        self.add_to_tabu(new_symbol)

        return new_symbol

    def purify_statistics_based_on_tabu(self, symbols_statistics):
        for symbol in self.tabu_queue:
            del symbols_statistics[symbol]

    def add_to_tabu(self, new_symbol):
        self.tabu_queue.append(new_symbol)
        if len(self.tabu_queue) > self.tabu_size:
            self.tabu_queue.popleft()
