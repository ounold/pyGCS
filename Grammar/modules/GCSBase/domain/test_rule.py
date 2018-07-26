from unittest import TestCase

from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType


class TestRule(TestCase):

    def setUp(self):
        self.left = Symbol("S", SymbolType.ST_START)
        self.rightTerminal = Symbol("R", SymbolType.ST_TERMINAL)
        self.leftTerminal = Symbol("L", SymbolType.ST_TERMINAL)
        self.leftNonTerminal = Symbol("L", SymbolType.ST_NON_TERMINAL)
        self.rightNonTerminal = Symbol("R", SymbolType.ST_NON_TERMINAL)

    def test_is_start(self):
        rule = Rule([self.left, self.rightTerminal])
        self.assertTrue(rule.is_start())

    def test_is_terminal(self):
        pass

    def test_is_non_terminal_one_right_symbol(self):
        rule = Rule([self.left, self.leftNonTerminal])
        self.assertTrue(rule.is_non_terminal())

    def test_is_non_terminal_two_right_symbols(self):
        rule = Rule([self.left, self.leftNonTerminal, self.rightNonTerminal])
        self.assertTrue(rule.is_non_terminal())

    def test_is_non_terminal_to_terminal_terminal_rule(self):
        rule = Rule([self.left, self.rightTerminal, self.rightTerminal])
        self.assertTrue(rule.is_non_terminal_to_terminal_terminal_rule())

    def test_is_non_terminal_to_terminal_terminal_rule_failure(self):
        rule = Rule([self.left, self.rightTerminal])
        self.assertFalse(rule.is_non_terminal_to_terminal_terminal_rule())

    def test_rule_equality(self):
        rule = Rule([self.left, self.rightTerminal])
        rule2 = Rule([self.left, self.rightTerminal])
        self.assertEqual(rule, rule2)

    def test_rule_not_equal_different_values_and_types(self):
        rule = Rule([self.left, self.rightTerminal])
        rule2 = Rule([self.left, self.leftNonTerminal])
        self.assertNotEqual(rule, rule2)

    def test_rule_not_equal_different_values(self):
        rule = Rule([self.left, self.rightTerminal])
        rule2 = Rule([self.left, self.leftTerminal])
        self.assertNotEqual(rule, rule2)

    def test_rule_not_equal_different_types(self):
        rule = Rule([self.left, self.rightTerminal])
        rule2 = Rule([self.left, self.rightNonTerminal])
        self.assertNotEqual(rule, rule2)
