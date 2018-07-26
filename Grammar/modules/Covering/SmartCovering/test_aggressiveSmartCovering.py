from unittest import TestCase
from unittest.mock import MagicMock

from modules.Covering.SmartCovering.aggressive_smart_covering import AggressiveSmartCovering
from modules.Crowding.standard_crowding import StandardCrowding
from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Visualisation.iteration import Iteration
from modules.sGCS.domain.sRule import sRule


class TestAggressiveSmartCovering(TestCase):

    def setUp(self):
        iteration = Iteration()
        self.crowding = StandardCrowding()
        self.crowding.set_iteration(iteration)
        self.covering = AggressiveSmartCovering(self.crowding)
        self.covering.set_iteration(iteration)
        self.symbol_v = Symbol('x', SymbolType.ST_TERMINAL)
        self.symbol_w = Symbol('w', SymbolType.ST_TERMINAL)
        self.symbol_x = Symbol('x', SymbolType.ST_TERMINAL)
        self.symbol_y = Symbol('y', SymbolType.ST_TERMINAL)
        self.symbol_z = Symbol('z', SymbolType.ST_TERMINAL)

        self.symbol_A = Symbol('A', SymbolType.ST_NON_TERMINAL)
        self.symbol_B = Symbol('B', SymbolType.ST_NON_TERMINAL)
        self.symbol_C = Symbol('C', SymbolType.ST_NON_TERMINAL)
        self.symbol_D = Symbol('D', SymbolType.ST_NON_TERMINAL)
        self.symbol_E = Symbol('E', SymbolType.ST_NON_TERMINAL)

        self.rule_1 = Rule([self.symbol_A, self.symbol_B, self.symbol_C])
        self.rule_2 = Rule([self.symbol_B, self.symbol_x, self.symbol_C])
        self.rule_3 = Rule([self.symbol_C, self.symbol_B, self.symbol_y])
        self.rule_4 = Rule([self.symbol_D, self.symbol_D, self.symbol_C])
        self.rule_5 = Rule([self.symbol_E, self.symbol_w])
        self.rule_6 = Rule([self.symbol_E, self.symbol_E])

        self.rules = [self.rule_1, self.rule_2, self.rule_3, self.rule_4, self.rule_5, self.rule_6]

        self.statistics = {self.symbol_A: 3, self.symbol_B: 7}

    def test_increment_statistic_for(self):
        self.covering.increment_statistic_for(self.symbol_C, self.statistics)
        self.assertEqual(self.statistics[self.symbol_C], 1)
        self.assertEqual(self.statistics[self.symbol_B], 7)
        self.assertEqual(self.statistics[self.symbol_A], 3)

        self.covering.increment_statistic_for(self.symbol_C, self.statistics)
        self.covering.increment_statistic_for(self.symbol_C, self.statistics)
        self.covering.increment_statistic_for(self.symbol_A, self.statistics)
        self.assertEqual(self.statistics[self.symbol_C], 3)
        self.assertEqual(self.statistics[self.symbol_B], 7)
        self.assertEqual(self.statistics[self.symbol_A], 4)

    def test_count_symbols_statistics(self):
        grammar = Grammar()
        grammar.get_rules = MagicMock(return_value=self.rules)
        result = self.covering.count_symbols_statistics(grammar)
        expected = {self.symbol_B: 2, self.symbol_C: 3, self.symbol_D: 1, self.symbol_E: 1}
        self.assertEqual(result, expected)

    def test_get_left_symbol_condition_true(self):
        grammar = Grammar()
        self.covering.find_left_symbol_wisely = MagicMock()
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock()

        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=True)
        self.covering.get_left_symbol(grammar)
        self.covering.find_left_symbol_wisely.assert_called_once_with(grammar)
        RandomUtils.get_random_nonterminal_symbol_from.assert_not_called()

    def test_get_left_symbol_condition_false(self):
        grammar = Grammar()
        self.covering.find_left_symbol_wisely = MagicMock()
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock()

        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=False)
        self.covering.get_left_symbol(grammar)
        self.covering.find_left_symbol_wisely.assert_not_called()
        RandomUtils.get_random_nonterminal_symbol_from.assert_called_once_with(grammar)

    def test_find_the_best_symbols(self):
        symbol_statistics = {self.symbol_A: 3, self.symbol_B: 7, self.symbol_E: 30, self.symbol_D: 1, self.symbol_C: 14}

        result = self.covering.find_the_best_symbols(symbol_statistics, 3)
        expected = [(self.symbol_E, 30), (self.symbol_C, 14), (self.symbol_B, 7)]
        self.assertEqual(3, len(result))
        self.assertEqual(expected, result)

        symbol_statistics = {self.symbol_A: 3}
        result = self.covering.find_the_best_symbols(symbol_statistics, 5)
        expected = [(self.symbol_A, 3)]
        self.assertEqual(1, len(result))
        self.assertEqual(expected, result)

    def test_find_left_symbol_wisely_condition_true(self):
        grammar = Grammar()
        self.covering.count_symbols_statistics = MagicMock(return_value={})
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock()
        self.covering.find_the_best_symbols = MagicMock()
        self.covering.roulette_selection.select = MagicMock()

        self.covering.find_left_symbol_wisely(grammar)

        RandomUtils.get_random_nonterminal_symbol_from.assert_called_once_with(grammar)
        self.covering.find_the_best_symbols.assert_not_called()
        self.covering.roulette_selection.select.assert_not_called()

    def test_find_left_symbol_wisely_condition_false(self):
        grammar = Grammar()
        self.covering.count_symbols_statistics = MagicMock(return_value=self.statistics)
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock()
        self.covering.find_the_best_symbols = MagicMock()
        self.covering.roulette_selection.select = MagicMock()

        self.covering.find_left_symbol_wisely(grammar)

        RandomUtils.get_random_nonterminal_symbol_from.assert_not_called()
        self.covering.find_the_best_symbols.assert_called_once_with(self.statistics, number_of_symbols=5)
        self.covering.roulette_selection.select.assert_called_once()

    def test_produce_rule(self):
        grammar = Grammar()
        self.covering.get_left_symbol = MagicMock(return_value=self.symbol_D)
        RandomUtils.get_random_probability = MagicMock(return_value=0.7)

        result = self.covering.produce_rule(grammar, self.symbol_C, self.symbol_x)
        expected = sRule.from_symbols(0.7, self.symbol_D, self.symbol_C, self.symbol_x)

        self.assertEqual(result, expected)

    def test_add_new_rule(self):
        grammar: Grammar = Grammar()
        self.covering.produce_rule = MagicMock(return_value=self.rule_1)
        self.covering.crowding.add_rule = MagicMock()
        result = self.covering.add_new_rule(grammar, self.symbol_C, self.symbol_D)
        self.assertEqual(self.rule_1, result)
        self.covering.crowding.add_rule.assert_called_once_with(grammar, self.rule_1)
