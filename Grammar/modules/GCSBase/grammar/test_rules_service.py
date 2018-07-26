from unittest import TestCase

from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.RulesService import RulesService


class RulesServiceTest(TestCase):

    def setUp(self):
        self.left = Symbol("S", SymbolType.ST_START)
        self.rightTerminal = Symbol("R", SymbolType.ST_TERMINAL)
        self.leftTerminal = Symbol("L", SymbolType.ST_TERMINAL)
        self.leftNonTerminal = Symbol("L", SymbolType.ST_NON_TERMINAL)
        self.rightNonTerminal = Symbol("R", SymbolType.ST_NON_TERMINAL)

    def test_rules_not_similar(self):
        rule = Rule([self.left, self.rightTerminal, self.rightNonTerminal])
        rule2 = Rule([self.leftTerminal, self.rightNonTerminal])
        similarities = RulesService.similarities_between_rules(rule, rule2)
        self.assertEqual(similarities, 0)

    def test_rules_similar_one_point_left(self):
        rule = Rule([self.left, self.rightTerminal, self.rightTerminal])
        rule2 = Rule([self.left, self.rightNonTerminal])
        similarities = RulesService.similarities_between_rules(rule, rule2)
        self.assertEqual(similarities, 1)

    def test_rules_similar_one_point_right1(self):
        rule = Rule([self.left, self.rightTerminal, self.rightTerminal])
        rule2 = Rule([self.leftTerminal, self.rightTerminal])
        similarities = RulesService.similarities_between_rules(rule, rule2)
        self.assertEqual(similarities, 1)

    def test_rules_similar_one_point_right2(self):
        rule = Rule([self.left, self.rightTerminal, self.rightTerminal])
        rule2 = Rule([self.leftTerminal, self.rightNonTerminal, self.rightTerminal])
        similarities = RulesService.similarities_between_rules(rule, rule2)
        self.assertEqual(similarities, 1)

    def test_rules_similar_two_points(self):
        rule = Rule([self.left, self.rightTerminal, self.rightTerminal])
        rule2 = Rule([self.left, self.rightNonTerminal, self.rightTerminal])
        similarities = RulesService.similarities_between_rules(rule, rule2)
        self.assertEqual(similarities, 2)

    def test_rules_similar_three_points(self):
        rule = Rule([self.left, self.rightNonTerminal, self.rightTerminal])
        rule2 = Rule([self.left, self.rightNonTerminal, self.rightTerminal])
        similarities = RulesService.similarities_between_rules(rule, rule2)
        self.assertEqual(similarities, 3)

    def test_descriptions_generation(self):
        rule = Rule([self.left, self.rightTerminal])
        rule.fitness = 1
        rule.profit = 2
        rule.usages_in_invalid_parsing = 3
        rule.usages_in_proper_parsing = 4
        rule.debt = 5
        rule.age = 6

        descriptions = RulesService.get_description_string_for_rule(rule)
        self.assertEqual(descriptions[0], "fitness (f): 1")
        self.assertEqual(descriptions[1], "proper usages (u_p): 4")
        self.assertEqual(descriptions[2], "invalid usages (u_n): 3")
        self.assertEqual(descriptions[3], "profit (p): 2")
        self.assertEqual(descriptions[4], "debt (d): 5")
        self.assertEqual(descriptions[5], "age: 6")