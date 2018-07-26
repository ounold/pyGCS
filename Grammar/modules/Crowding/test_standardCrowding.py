from typing import List
from unittest import TestCase
from unittest.mock import MagicMock

from modules.Crowding.standard_crowding import StandardCrowding
from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.AaaRulesHandlingType import AaaRulesHandlingType
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.RulesService import RulesService
from modules.GCSBase.grammar.grammar import Grammar
from settings.settings import Settings


class TestStandardCrowding(TestCase):

    def setUp(self):
        self.crowding = StandardCrowding()
        self.rule_1 = self.__create_rule(["a", "b", "c"], 100.5)
        self.rule_2 = self.__create_rule(["d", "e", "f"], 50.5)
        self.rule_3 = self.__create_rule(["g", "h", "i"], 25.5)
        self.rule_4 = self.__create_rule(["j", "k", "l"], 12.5)
        self.rule_5 = self.__create_rule(["m", "n", "o"], 6.5)
        self.rules = [self.rule_2, self.rule_5, self.rule_3, self.rule_1, self.rule_4]

        self.new_rule_1 = self.__create_rule(["x", "y", "z"])
        self.new_rule_2 = self.__create_rule(["q", "w", "e"])
        self.new_rule_3 = self.__create_rule(["a", "s", "d"])
        self.new_rules = [self.new_rule_1, self.new_rule_2, self.new_rule_3]

    def test_rule_already_exist(self):
        rule = self.__create_rule(["a", "b", "c"])
        result = self.crowding.rule_already_exist(rule, self.rules)
        self.assertTrue(result)

        rule = self.__create_rule(["x", "y", "z"])
        result = self.crowding.rule_already_exist(rule, self.rules)
        self.assertFalse(result)

    def test_grammar_has_room_for_rule(self):
        self.crowding.non_terminal_productions_number = 100
        result = self.crowding.grammar_has_room_for_rule(self.rules)
        self.assertTrue(result)

        self.crowding.non_terminal_productions_number = 2
        result = self.crowding.grammar_has_room_for_rule(self.rules)
        self.assertFalse(result)

    def test_remove_the_best_rules_when_elite_number_right(self):
        self.crowding.settings = Settings('')
        self.crowding.settings.get_value = MagicMock(return_value=2)
        self.crowding.elite_rules_number = 2
        rules = self.crowding.remove_the_best_rules(self.rules)
        self.assertTrue(rules.__contains__(self.rule_5))
        self.assertTrue(rules.__contains__(self.rule_4))
        self.assertTrue(rules.__contains__(self.rule_3))
        self.assertFalse(rules.__contains__(self.rule_2))
        self.assertFalse(rules.__contains__(self.rule_1))

    def test_remove_the_best_rules_when_elite_number_too_big(self):
        self.crowding.settings = Settings('')
        self.crowding.settings.get_value = MagicMock(return_value=200)
        self.crowding.elite_rules_number = 200
        rules = self.crowding.remove_the_best_rules(self.rules)
        self.assertEqual(len(rules), 0)

    def test_find_the_worst(self):
        rule = self.crowding.find_the_worst(self.rules)
        self.assertEqual(rule, self.rule_5)

    def test_create_random_subset(self):
        subset = self.crowding.create_random_subset(self.rules, size=2)
        self.assertEqual(len(subset), 2)
        self.assertEqual(len(self.rules), 5)

    def test_find_the_most_similar_to(self):
        RulesService.similarities_between_rules = MagicMock(side_effect=[32, 16, 64, 8, 4])
        rule = self.__create_rule(["x", "y", "z"])
        found_rule = self.crowding.find_the_most_similar_to(rule, self.rules)
        self.assertEqual(found_rule, self.rule_3)
        self.assertNotEqual(found_rule, self.rule_5)

    def initialize_rules(self):
        self.crowding.is_non_terminal_type = MagicMock(return_value=True)
        self.crowding.filter_non_terminal_to_terminal_terminal_rule = MagicMock()
        grammar = Grammar()
        grammar.get_non_terminal_rules = MagicMock(return_value=self.rules)
        rule = self.__create_rule(["x", "y", "z"])

        self.crowding.initialize_rules(rule, grammar)
        self.crowding.filter_non_terminal_to_terminal_terminal_rule.assert_called_once_with(self.rules)

        self.crowding.is_non_terminal_type = MagicMock(return_value=False)
        result = self.crowding.initialize_rules(rule, grammar)
        self.assertEqual(result, self.rules)

    def test_is_non_terminal_type(self):
        self.crowding.aaa_rules_handling_type = AaaRulesHandlingType.NON_TERMINALS
        self.crowding.non_terminal_productions_number = 20
        rule = self.__create_rule(["x", "y", "z"])
        rule.is_non_terminal_to_terminal_terminal_rule = MagicMock(return_value=False)
        grammar = Grammar()
        grammar.count_Aaa_rules = MagicMock(return_value=10)

        self.assertTrue(self.crowding.is_non_terminal_type(rule, grammar))

        rule.is_non_terminal_to_terminal_terminal_rule = MagicMock(return_value=True)
        self.assertFalse(self.crowding.is_non_terminal_type(rule, grammar))

        self.crowding.aaa_rules_handling_type = 'TERMINALS'
        self.assertFalse(self.crowding.is_non_terminal_type(rule, grammar))

        self.crowding.non_terminal_productions_number = 5
        self.assertFalse(self.crowding.is_non_terminal_type(rule, grammar))

    def test_filter_non_terminal_to_terminal_terminal_rule(self):
        symbols = [Symbol('x', SymbolType.ST_TERMINAL),
                   Symbol('y', SymbolType.ST_NON_TERMINAL),
                   Symbol('z', SymbolType.ST_NON_TERMINAL)]
        rule = Rule(symbols)

        result = self.crowding.filter_non_terminal_to_terminal_terminal_rule(self.rules)
        self.assertEqual(result, set())

        result = self.crowding.filter_non_terminal_to_terminal_terminal_rule(self.rules + [rule])
        self.assertEqual(result, {rule})

    def test_count_group_similarity(self):
        RulesService.similarities_between_rules = MagicMock(side_effect=[32, 16, 64, 8, 4])
        result = self.crowding.count_group_similarity(Rule(), self.rules)
        self.assertEqual(result, 124)

    def test_grammar_has_room_for_rules(self):
        self.crowding.non_terminal_productions_number = 20
        new_rule_1 = self.__create_rule(["x", "y", "z"], 100.5)
        new_rule_2 = self.__create_rule(["q", "w", "e"], 100.5)

        result = self.crowding.grammar_has_room_for_rules([new_rule_1, new_rule_2], self.rules)
        self.assertTrue(result)

        self.crowding.non_terminal_productions_number = 7
        result = self.crowding.grammar_has_room_for_rules([new_rule_1, new_rule_2], self.rules)
        self.assertTrue(result)

        self.crowding.non_terminal_productions_number = 5
        result = self.crowding.grammar_has_room_for_rules([new_rule_1, new_rule_2], self.rules)
        self.assertFalse(result)

    def test_count_rules_to_remove(self):
        self.crowding.non_terminal_productions_number = 5
        result = self.crowding.count_rules_to_remove(self.new_rules, self.rules)
        self.assertEqual(result, 3)

        self.crowding.non_terminal_productions_number = 8
        result = self.crowding.count_rules_to_remove(self.new_rules, self.rules)
        self.assertEqual(result, 0)

    def test_find_the_most_similar_from(self):
        self.crowding.count_group_similarity = MagicMock(side_effect=self.new_rules_side_effect)
        result = self.crowding.find_the_most_similar_from(self.new_rules, self.rules)
        self.assertEqual(result, self.rule_1)

    def test_find_the_worst_rules(self):
        self.crowding.crowding_population = 2
        self.crowding.crowding_factor = 3
        side_effect = [[self.rule_1, self.rule_5], [self.rule_2, self.rule_3], [self.rule_3, self.rule_4]]
        self.crowding.create_random_subset = MagicMock(side_effect=side_effect)
        result = self.crowding.find_the_worst_rules(self.rules)
        self.assertEqual(result, [self.rule_5, self.rule_3, self.rule_4])

    @staticmethod
    def __create_rule(symbols, fitness: float = None) -> Rule:
        symbols = [Symbol(symbols[0], SymbolType.ST_NON_TERMINAL),
                   Symbol(symbols[1], SymbolType.ST_TERMINAL),
                   Symbol(symbols[2], SymbolType.ST_TERMINAL)]
        rule = Rule(symbols)
        if fitness:
            rule.fitness = fitness
        return rule

    def new_rules_side_effect(self, rule: Rule, rules: List[Rule]) -> int:
        if rule == self.rule_1:
            return 100
        elif rule == self.rule_2:
            return 50
        elif rule == self.rule_3:
            return 25
        elif rule == self.rule_4:
            return 12
        elif rule == self.rule_5:
            return 6
