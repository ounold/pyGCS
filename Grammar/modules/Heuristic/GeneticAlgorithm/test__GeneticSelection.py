import random
from unittest import TestCase
from unittest.mock import MagicMock

from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.Heuristic.GeneticAlgorithm.genetic_algorithm import _GeneticSelection, GeneticSelectionType


class Test_GeneticSelection(TestCase):

    def setUp(self):
        self.genetic_selection = _GeneticSelection()

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

        self.rule_1.fitness = 9
        self.rule_2.fitness = 12
        self.rule_3.fitness = 15
        self.rule_4.fitness = 6
        self.rule_5.fitness = 3

        self.rules = {self.rule_1, self.rule_2, self.rule_3, self.rule_4, self.rule_5}
        self.rules_list = [self.rule_1, self.rule_2, self.rule_3, self.rule_4, self.rule_5]


    def test_prepare_selection_map(self):
        result = self.genetic_selection.prepare_selection_map()
        expected = {GeneticSelectionType.RANDOM: self.genetic_selection.random_select,
                    GeneticSelectionType.TOURNAMENT: self.genetic_selection.tournament_select,
                    GeneticSelectionType.ROULETTE: self.genetic_selection.roulette_select}
        self.assertEqual(expected, result)

    def test_select_rule(self):
        grammar = MagicMock()
        grammar.get_non_terminal_rules = MagicMock(return_value=self.rules)
        result = self.genetic_selection.select_rule(grammar, GeneticSelectionType.TOURNAMENT)
        self.assertIsNotNone(result)

    def test_random_select(self):
        result: Rule = self.genetic_selection.random_select(self.rules)
        self.assertIsNotNone(result)

        self.genetic_selection.random_select = MagicMock(return_value=self.rule_1)
        result = self.genetic_selection.random_select(self.rules)
        self.assertEqual(self.rule_1, result)
        self.genetic_selection.random_select.assert_called_once_with(self.rules)

    def test_tournament_select(self):
        self.genetic_selection.tournament_subpopulation_size = 2
        result = self.genetic_selection.tournament_select(self.rules)
        self.assertIsNotNone(result)

        self.genetic_selection._choose_random_subpopulation = MagicMock(return_value=[self.rule_1, self.rule_2])
        self.genetic_selection._find_the_best_rule = MagicMock(return_value=self.rule_2)
        result = self.genetic_selection.tournament_select(self.rules)
        self.assertEqual(self.rule_2, result)
        self.genetic_selection._choose_random_subpopulation.assert_called_once_with(self.rules, 2)
        self.genetic_selection._find_the_best_rule.assert_called_once_with([self.rule_1, self.rule_2])

    def test__choose_random_subpopulation(self):
        result = self.genetic_selection._choose_random_subpopulation(self.rules, 4)
        self.assertEqual(4, len(result))

        random.sample = MagicMock(return_value=[self.rule_1, self.rule_2])
        result = self.genetic_selection._choose_random_subpopulation(self.rules, 2)
        self.assertEqual([self.rule_1, self.rule_2], result)
        random.sample.assert_called_once_with(self.rules, 2)

    def test__find_the_best_rule(self):
        result = self.genetic_selection._find_the_best_rule(list(self.rules))
        self.assertEqual(self.rule_3, result)

    def test___sum_fitness(self):
        result = self.genetic_selection._sum_fitness(self.rules_list)
        self.assertEqual(45, result)

    def test__count_sections_of_roulette_wheel(self):
        result = self.genetic_selection._count_sections_of_roulette_wheel(self.rules_list)
        self.assertEqual([9, 21, 36, 42, 45], result)

    def test__find_rule_when_wheel_point_3(self):
        result = self.genetic_selection._find_rule(self.rules_list, [9, 21, 36, 42, 45], 3)
        self.assertEqual(self.rule_1, result)

    def test__find_rule_when_wheel_point_45(self):
        result = self.genetic_selection._find_rule(self.rules_list, [9, 21, 36, 42, 45], 44)
        self.assertEqual(self.rule_5, result)

    def test__find_rule_when_wheel_point_0(self):
        result = self.genetic_selection._find_rule(self.rules_list, [9, 21, 36, 42, 45], 0)
        self.assertEqual(self.rule_1, result)

    def test_roulette_select(self):
        result = self.genetic_selection.roulette_select(self.rules)
        self.assertIsNotNone(result)

    def test_roulette_select_when_wheel_point_18(self):
        self.genetic_selection._rules_set_to_list = MagicMock(return_value=self.rules_list)
        random.randint = MagicMock(return_value=18)
        result = self.genetic_selection.roulette_select(self.rules)

        self.assertEqual(self.rule_2, result)

    def test_roulette_select_when_wheel_point_40(self):
        self.genetic_selection._rules_set_to_list = MagicMock(return_value=self.rules_list)
        random.randint = MagicMock(return_value=40)
        result = self.genetic_selection.roulette_select(self.rules)

        self.assertEqual(self.rule_4, result)

    def test_roulette_select_when_wheel_point_20(self):
        self.genetic_selection._rules_set_to_list = MagicMock(return_value=self.rules_list)
        random.randint = MagicMock(return_value=20)
        result = self.genetic_selection.roulette_select(self.rules)

        self.assertEqual(self.rule_2, result)
