import copy
from unittest import TestCase
from unittest.mock import MagicMock, call

from modules.Crowding.crowding import Crowding
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Heuristic.GeneticAlgorithm.genetic_algorithm import GeneticAlgorithm, GeneticSelectionType, CrossoverReport
from modules.sGCS.domain.sRule import sRule
from settings.settings import Settings


class TestGeneticAlgorithm(TestCase):

    def setUp(self):
        self.genetic_algorithm = GeneticAlgorithm(Crowding(), None)
        self.grammar = Grammar()

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

        self.rule_1 = sRule.from_symbols(0.1, self.symbol_A, self.symbol_B, self.symbol_C)
        self.rule_2 = sRule.from_symbols(0.5, self.symbol_B, self.symbol_x, self.symbol_C)
        self.rule_3 = sRule.from_symbols(0.4, self.symbol_C, self.symbol_B, self.symbol_y)
        self.rule_4 = sRule.from_symbols(0.9, self.symbol_D, self.symbol_D, self.symbol_C)
        self.rule_5 = sRule.from_symbols(0.2, self.symbol_E, self.symbol_w)

        self.rule_1.fitness = 9
        self.rule_2.fitness = 12
        self.rule_3.fitness = 15
        self.rule_4.fitness = 6
        self.rule_5.fitness = 3

        self.rules = {self.rule_1, self.rule_2, self.rule_3, self.rule_4, self.rule_5}
        self.rules_list = [self.rule_1, self.rule_2, self.rule_3, self.rule_4, self.rule_5]
        self.grammar.get_non_terminal_rules = MagicMock(return_value=self.rules)
        self.random_decision = RandomUtils.make_random_decision_with_probability
        self.random_non_terminal = RandomUtils.get_random_nonterminal_symbol_from

    def tearDown(self):
        RandomUtils.make_random_decision_with_probability = self.random_decision
        RandomUtils.get_random_nonterminal_symbol_from = self.random_non_terminal

    def test_run(self):
        self.genetic_algorithm.add_to_iteration = MagicMock()
        self.genetic_algorithm.select = MagicMock(return_value=(self.rule_1, self.rule_2))
        self.genetic_algorithm.crossover = MagicMock(return_value=(self.rule_3, self.rule_4, CrossoverReport()))
        self.genetic_algorithm.invert = MagicMock()
        self.genetic_algorithm.mutate = MagicMock()

        self.genetic_algorithm.run(self.grammar)

        self.genetic_algorithm.select.assert_called_once_with(self.grammar)
        self.genetic_algorithm.crossover.assert_called_once_with((self.rule_1, self.rule_2))
        self.genetic_algorithm.invert.assert_has_calls([call(self.rule_3), call(self.rule_4)])
        self.genetic_algorithm.mutate.assert_has_calls(
            [call(self.rule_3, self.grammar), call(self.rule_4, self.grammar)])

    def test_select(self):
        self.genetic_algorithm.first_rule_selection_type = GeneticSelectionType.TOURNAMENT
        self.genetic_algorithm.second_rule_selection_type = GeneticSelectionType.RANDOM
        result = self.genetic_algorithm.select(self.grammar)
        self.assertIsNotNone(result[0])
        self.assertIsNotNone(result[1])

    def test_select_when_selection_type_is_tournament_and_random(self):
        self.genetic_algorithm.first_rule_selection_type = GeneticSelectionType.TOURNAMENT
        self.genetic_algorithm.second_rule_selection_type = GeneticSelectionType.RANDOM
        self.genetic_algorithm.selection.select_rule = MagicMock(side_effect=[self.rule_1, self.rule_5])

        result = self.genetic_algorithm.select(self.grammar)

        calls = [call(self.grammar, GeneticSelectionType.TOURNAMENT),
                 call(self.grammar, GeneticSelectionType.RANDOM)]
        self.genetic_algorithm.selection.select_rule.assert_has_calls(calls)
        self.assertIs(self.rule_1, result[0])
        self.assertIs(self.rule_5, result[1])

    def test_invert_when_random_decision_false(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=False)
        self.genetic_algorithm.inversion_probability = 0.12345
        self.genetic_algorithm.invert_rule = MagicMock()
        self.genetic_algorithm.adjust_rules_after_inverse = MagicMock()
        rule_copy = copy.deepcopy(self.rule_1)

        self.genetic_algorithm.invert(self.rule_1)

        self.assertEqual(self.rule_1, rule_copy)
        self.genetic_algorithm.invert_rule.assert_not_called()
        self.genetic_algorithm.adjust_rules_after_inverse.assert_not_called()
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.12345)

    def test_invert_when_random_decision_true(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=True)
        self.genetic_algorithm.inversion_probability = 0.12345
        self.genetic_algorithm.invert_rule = MagicMock()
        self.genetic_algorithm.adjust_rules_after_inverse = MagicMock()

        self.genetic_algorithm.invert(self.rule_1)

        self.genetic_algorithm.invert_rule.assert_called_once_with(self.rule_1)
        self.genetic_algorithm.adjust_rules_after_inverse.assert_called_once_with(self.rule_1)
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.12345)

    def test_invert_rule_when_second_right_symbol_empty(self):
        rule_copy = copy.deepcopy(self.rule_5)
        self.genetic_algorithm.invert_rule(self.rule_5)
        self.assertEqual(rule_copy, self.rule_5)

    def test_invert_rule_when_second_right_symbol_exist(self):
        first_right = self.rule_1.right1
        second_right = self.rule_1.right2
        self.genetic_algorithm.invert_rule(self.rule_1)
        self.assertEqual(second_right, self.rule_1.right1)
        self.assertEqual(first_right, self.rule_1.right2)

    def test_adjust_rules_after_inverse_when_rule_count_0(self):
        rule_s = sRule.from_symbols(0.1, self.symbol_A, self.symbol_B, self.symbol_C)
        rule_s.count, rule_s.positive_count, rule_s.negative_count = 0, 10, 20

        expected = sRule.from_symbols(0.9, self.symbol_A, self.symbol_B, self.symbol_C)

        self.genetic_algorithm.adjust_rules_after_inverse(rule_s)

        self.assertEqual(expected, rule_s)
        self.assertEqual(0, rule_s.count)
        self.assertEqual(0, rule_s.positive_count)
        self.assertEqual(0, rule_s.negative_count)

    def test_adjust_rules_after_inverse_when_rule_count_different_then_0(self):
        rule_s = sRule.from_symbols(0.1, self.symbol_A, self.symbol_B, self.symbol_C)
        rule_s.count, rule_s.positive_count, rule_s.negative_count = 10, 20, 50
        expected = sRule.from_symbols(0.9, self.symbol_A, self.symbol_B, self.symbol_C)

        self.genetic_algorithm.adjust_rules_after_inverse(rule_s)

        self.assertEqual(expected, rule_s)
        self.assertEqual(0.1, rule_s.count)
        self.assertEqual(0.05, rule_s.positive_count)
        self.assertEqual(0.02, rule_s.negative_count)

    def test_mutate(self):
        self.genetic_algorithm.mutate_symbol = MagicMock(side_effect=[self.symbol_A, self.symbol_B, self.symbol_x])
        rule_copy = copy.deepcopy(self.rule_1)

        self.genetic_algorithm.mutate(self.rule_1, self.grammar)

        calls = [call(rule_copy.left, self.grammar),
                 call(rule_copy.right1, self.grammar),
                 call(rule_copy.right2, self.grammar)]
        self.genetic_algorithm.mutate_symbol.assert_has_calls(calls)

    def test_mutate_symbol_random_decision_false(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=False)
        self.genetic_algorithm.mutation_probability = 0.12345
        result = self.genetic_algorithm.mutate_symbol(self.symbol_A, self.grammar)
        self.assertEqual(self.symbol_A, result)
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.12345)

    def test_mutate_symbol_random_decision_true(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=True)
        self.genetic_algorithm.mutation_probability = 0.12345
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock(return_value=self.symbol_E)
        result = self.genetic_algorithm.mutate_symbol(self.symbol_A, self.grammar)
        self.assertEqual(self.symbol_E, result)
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.12345)

    def test_mutate_symbol_when_symbols_list_empty(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=True)
        self.genetic_algorithm.mutation_probability = 0.12345
        self.grammar.nonTerminalSymbols = []
        result = self.genetic_algorithm.mutate_symbol(self.symbol_B, self.grammar)
        self.assertEqual(self.symbol_B, result)
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.12345)


    def test_add_to_grammar(self):
        self.genetic_algorithm.crowding.add_rule = MagicMock(return_value=True)
        self.genetic_algorithm.iteration.add_ga_first_rule = MagicMock()
        self.genetic_algorithm.iteration.add_ga_second_rule = MagicMock()
        self.genetic_algorithm.add_to_grammar((self.rule_1, self.rule_2), self.grammar)
        calls = [call(self.grammar, self.rule_1), call(self.grammar, self.rule_2)]
        self.genetic_algorithm.crowding.add_rule.assert_has_calls(calls)

    def test_crossover_random_decision_false(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=False)
        self.genetic_algorithm.crossing_probability = 0.12345
        self.genetic_algorithm.cross_rules = MagicMock()
        self.genetic_algorithm.adjust_rules_after_crossover = MagicMock()

        result = self.genetic_algorithm.crossover((self.rule_1, self.rule_2))

        self.assertEqual((self.rule_1, self.rule_2), (result[0], result[1]))
        self.assertIsNot(self.rule_1, result[0])
        self.assertIsNot(self.rule_2, result[1])
        self.genetic_algorithm.cross_rules.assert_not_called()
        self.genetic_algorithm.adjust_rules_after_crossover.assert_not_called()
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.12345)

    def test_crossover_random_when_decision_true(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=True)
        self.genetic_algorithm.cross_rules = MagicMock()
        self.genetic_algorithm.adjust_rules_after_crossover = MagicMock()
        self.genetic_algorithm.crossing_probability = 0.12345

        result = self.genetic_algorithm.crossover((self.rule_1, self.rule_2))

        self.assertEqual((self.rule_1, self.rule_2), (result[0], result[1]))
        self.assertIsNot(self.rule_1, result[0])
        self.assertIsNot(self.rule_2, result[1])
        self.genetic_algorithm.cross_rules.assert_called_once_with((self.rule_1, self.rule_2))
        self.genetic_algorithm.adjust_rules_after_crossover.assert_called_once_with((self.rule_1, self.rule_2))
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.12345)

    def test_cross_rules_when_decision_false(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=False)
        copy_rule_2 = copy.deepcopy(self.rule_2)
        copy_rule_2.right2 = self.symbol_y
        copy_rule_3 = copy.deepcopy(self.rule_3)
        copy_rule_3.right2 = self.symbol_C

        self.genetic_algorithm.cross_rules((self.rule_2, self.rule_3))

        self.assertEqual((copy_rule_2, copy_rule_3), (self.rule_2, self.rule_3))
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.5)

    def test_cross_rules_when_decision_true(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=True)
        copy_rule_2 = copy.deepcopy(self.rule_2)
        copy_rule_2.right1 = self.symbol_B
        copy_rule_3 = copy.deepcopy(self.rule_3)
        copy_rule_3.right1 = self.symbol_x

        self.genetic_algorithm.cross_rules((self.rule_2, self.rule_3))

        self.assertEqual((copy_rule_2, copy_rule_3), (self.rule_2, self.rule_3))
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.5)

    def test_cross_rules_when_second_right_symbol_empty(self):
        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=False)
        copy_rule_2 = copy.deepcopy(self.rule_2)
        copy_rule_2.right2 = None
        copy_rule_5 = copy.deepcopy(self.rule_5)
        copy_rule_5.right2 = self.symbol_C

        self.genetic_algorithm.cross_rules((self.rule_2, self.rule_5))

        self.assertEqual((copy_rule_2, copy_rule_5), (self.rule_2, self.rule_5))
        RandomUtils.make_random_decision_with_probability.assert_called_once_with(0.5)

    def test_adjust_rules_after_crossover(self):
        s_rule_x = sRule.from_symbols(0.1, self.symbol_A, self.symbol_B, self.symbol_C)
        s_rule_y = sRule.from_symbols(0.7, self.symbol_D, self.symbol_E, self.symbol_x)
        s_rule_x.count, s_rule_x.positive_count, s_rule_x.negative_count = 10, 20, 30
        s_rule_y.count, s_rule_y.positive_count, s_rule_y.negative_count = 15, 25, 35
        expected_1 = sRule.from_symbols(0.7, self.symbol_A, self.symbol_B, self.symbol_C)
        expected_2 = sRule.from_symbols(0.1, self.symbol_D, self.symbol_E, self.symbol_x)

        self.genetic_algorithm.adjust_rules_after_crossover((s_rule_x, s_rule_y))

        self.assertEqual(expected_1, s_rule_x)
        self.assertEqual(expected_2, s_rule_y)
        self.assertEqual([s_rule_x.count, s_rule_x.positive_count, s_rule_x.negative_count], [15, 25, 35])
        self.assertEqual([s_rule_y.count, s_rule_y.positive_count, s_rule_y.negative_count], [10, 20, 30])

    def test_add_new_rules(self):
        self.genetic_algorithm.run = MagicMock(return_value=(self.rule_1, self.rule_2))
        self.genetic_algorithm.add_to_grammar = MagicMock()
        self.genetic_algorithm.add_new_rules(self.grammar)
        self.genetic_algorithm.run.assert_called_once_with(self.grammar)
        self.genetic_algorithm.run.add_to_grammar((self.rule_1, self.rule_2))
