from collections import deque
from unittest import TestCase
from unittest.mock import MagicMock

from modules.Covering.SmartCoveringWithTabu.aggressive_smart_covering_with_tabu import \
    AggressiveSmartCoveringWithTabu
from modules.Crowding.standard_crowding import StandardCrowding
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Visualisation.iteration import Iteration


class TestAggressiveSmartCoveringWithTabu(TestCase):

    def setUp(self):
        iteration = Iteration()
        self.crowding = StandardCrowding()
        self.crowding.set_iteration(iteration)
        self.covering = AggressiveSmartCoveringWithTabu(self.crowding)
        self.covering.set_iteration(iteration)

        self.symbol_A = Symbol('A', SymbolType.ST_NON_TERMINAL)
        self.symbol_B = Symbol('B', SymbolType.ST_NON_TERMINAL)
        self.symbol_C = Symbol('C', SymbolType.ST_NON_TERMINAL)
        self.symbol_D = Symbol('D', SymbolType.ST_NON_TERMINAL)
        self.symbol_E = Symbol('E', SymbolType.ST_NON_TERMINAL)

        self.statistics = {self.symbol_A: 3, self.symbol_B: 7}

    def test_purify_statistics_based_on_tabu(self):
        statistics = {self.symbol_A: 3, self.symbol_B: 7, self.symbol_C: 5, self.symbol_D: 18, self.symbol_E: 45}
        self.covering.tabu_queue = deque([self.symbol_A, self.symbol_C, self.symbol_E])
        expected = {self.symbol_B: 7, self.symbol_D: 18}

        self.covering.purify_statistics_based_on_tabu(statistics)
        self.assertEqual(expected, statistics)

    def test_add_to_tabu(self):
        self.covering.tabu_queue = deque([self.symbol_A, self.symbol_B, self.symbol_C])
        self.covering.tabu_size = 10

        self.covering.add_to_tabu(self.symbol_D)
        expected = deque([self.symbol_A, self.symbol_B, self.symbol_C, self.symbol_D])
        self.assertEqual(expected, self.covering.tabu_queue)

        self.covering.tabu_queue = deque([self.symbol_A, self.symbol_B, self.symbol_C])
        self.covering.tabu_size = 3

        self.covering.add_to_tabu(self.symbol_D)
        expected = deque([self.symbol_B, self.symbol_C, self.symbol_D])
        self.assertEqual(expected, self.covering.tabu_queue)

    def test_find_left_symbol_wisely_condition_true(self):
        grammar = Grammar()
        self.covering.count_symbols_statistics = MagicMock(return_value={})
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock()
        self.covering.find_the_best_symbols = MagicMock()
        self.covering.roulette_selection.select = MagicMock()
        self.covering.purify_statistics_based_on_tabu = MagicMock()
        self.covering.add_to_tabu = MagicMock()

        self.covering.find_left_symbol_wisely(grammar)

        RandomUtils.get_random_nonterminal_symbol_from.assert_called_once_with(grammar)
        self.covering.find_the_best_symbols.assert_not_called()
        self.covering.roulette_selection.select.assert_not_called()
        self.covering.purify_statistics_based_on_tabu.assert_not_called()
        self.covering.add_to_tabu.assert_not_called()

    def test_find_left_symbol_wisely_condition_false(self):
        grammar = Grammar()
        self.covering.count_symbols_statistics = MagicMock(return_value=self.statistics)
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock()
        self.covering.find_the_best_symbols = MagicMock()
        self.covering.roulette_selection.select = MagicMock(return_value=self.symbol_D)
        self.covering.purify_statistics_based_on_tabu = MagicMock()
        self.covering.add_to_tabu = MagicMock()

        self.covering.find_left_symbol_wisely(grammar)

        RandomUtils.get_random_nonterminal_symbol_from.assert_not_called()
        self.covering.find_the_best_symbols.assert_called_once_with(self.statistics, number_of_symbols=5)
        self.covering.roulette_selection.select.assert_called_once()
        self.covering.purify_statistics_based_on_tabu.assert_called_once_with(self.statistics)
        self.covering.add_to_tabu.assert_called_once_with(self.symbol_D)
