from unittest import TestCase
from unittest.mock import MagicMock

from modules.Covering.NakamuraCovering.nakamura_covering import NakamuraCovering
from modules.Crowding.standard_crowding import StandardCrowding
from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Visualisation.iteration import Iteration
from modules.sGCS.domain.sRule import sRule


class TestNakamuraCovering(TestCase):

    def setUp(self):
        iteration = Iteration()
        self.crowding = StandardCrowding()
        self.crowding.set_iteration(iteration)
        self.covering = NakamuraCovering(self.crowding)
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
        self.rule_6 = Rule([self.symbol_E, self.symbol_D])

        self.rules = [self.rule_1, self.rule_2, self.rule_3, self.rule_4, self.rule_5, self.rule_6]

    def test_rule_is_effective(self):
        grammar = Grammar()
        grammar.get_rules = MagicMock(return_value=self.rules)
        rule = Rule([self.symbol_C, self.symbol_B, self.symbol_x])
        result = self.covering.rule_is_effective(grammar, rule.left)
        self.assertTrue(result)

        rule = Rule([self.symbol_E, self.symbol_B, self.symbol_x])
        result = self.covering.rule_is_effective(grammar, rule.left)
        self.assertFalse(result)

    def test_produce_rule_based_on_random_decision(self):
        grammar = Grammar()
        RandomUtils.get_random_probability = MagicMock(return_value=0.9)
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock(return_value=self.symbol_A)

        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=True)
        result: sRule = self.covering.produce_rule_based_on_random_decision(grammar, self.symbol_x)
        expected: sRule = sRule.from_symbols(0.9, self.symbol_A, self.symbol_x, self.symbol_A)

        self.assertEqual(expected, result)

        RandomUtils.make_random_decision_with_probability = MagicMock(return_value=False)
        result: sRule = self.covering.produce_rule_based_on_random_decision(grammar, self.symbol_x)
        expected: sRule = sRule.from_symbols(0.9, self.symbol_A, self.symbol_A, self.symbol_x)

        self.assertEqual(expected, result)

    def test_make_rule_effective(self):
        grammar = Grammar()
        self.covering.rule_is_effective = MagicMock(side_effect=4 * [False] + [True])
        self.covering.produce_rule_based_on_random_decision = MagicMock(
            side_effect=[self.rule_1, self.rule_2, self.rule_3, self.rule_4])
        self.covering.crowding.add_rule = MagicMock()
        self.covering.crowding.add_rules = MagicMock()

        self.covering.make_rule_effective(grammar, self.rule_1)

        self.assertEqual(self.covering.rule_is_effective.call_count, 5)
        self.assertEqual(self.covering.produce_rule_based_on_random_decision.call_count, 4)
        self.assertEqual(self.covering.crowding.add_rule.call_count, 4)
        self.covering.crowding.add_rules.assert_called_once()

    def test_produce_rule(self):
        grammar = Grammar()
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock(return_value=self.symbol_D)
        RandomUtils.get_random_probability = MagicMock(return_value=0.7)

        result = self.covering.produce_rule(grammar, self.symbol_C)
        expected = sRule.from_symbols(0.7, self.symbol_D, self.symbol_C)

        self.assertEqual(result, expected)
