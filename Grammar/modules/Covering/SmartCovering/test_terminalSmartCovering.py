from unittest import TestCase
from unittest.mock import MagicMock

from modules.Covering.SmartCovering.terminal_smart_covering import TerminalSmartCovering
from modules.Crowding.standard_crowding import StandardCrowding
from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Visualisation.iteration import Iteration
from modules.sGCS.domain.sRule import sRule


class TestTerminalSmartCovering(TestCase):

    def setUp(self):
        iteration = Iteration()
        self.crowding = StandardCrowding()
        self.crowding.set_iteration(iteration)
        self.covering = TerminalSmartCovering(self.crowding)
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

    def test_produce_rule(self):
        grammar = Grammar()
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock(return_value=self.symbol_D)
        RandomUtils.get_random_probability = MagicMock(return_value=0.7)

        result = self.covering.produce_rule(grammar, self.symbol_C)
        expected = sRule.from_symbols(0.7, self.symbol_D, self.symbol_C)

        self.assertEqual(result, expected)

    def test_add_new_rule(self):
        grammar: Grammar = Grammar()
        self.covering.produce_rule = MagicMock(return_value=self.rule_1)
        self.covering.crowding.add_rule = MagicMock()

        result = self.covering.add_new_rule(grammar, self.symbol_C)
        self.assertEqual(self.rule_1, result)
        self.covering.crowding.add_rule.assert_called_once_with(grammar, self.rule_1)
