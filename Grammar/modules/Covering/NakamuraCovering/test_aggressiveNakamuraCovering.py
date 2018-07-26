from unittest import TestCase
from unittest.mock import MagicMock

from modules.Covering.NakamuraCovering.aggressive_nakamura_covering import AggressiveNakamuraCovering
from modules.Crowding.standard_crowding import StandardCrowding
from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.Visualisation.iteration import Iteration


class TestAggressiveNakamuraCovering(TestCase):

    def setUp(self):
        iteration = Iteration()
        self.crowding = StandardCrowding()
        self.crowding.set_iteration(iteration)
        self.covering = AggressiveNakamuraCovering(self.crowding)
        self.covering.set_iteration(iteration)

        self.symbol_A = Symbol('A', SymbolType.ST_NON_TERMINAL)
        self.symbol_B = Symbol('B', SymbolType.ST_NON_TERMINAL)
        self.symbol_C = Symbol('C', SymbolType.ST_NON_TERMINAL)

        self.rule_1 = Rule([self.symbol_A, self.symbol_B, self.symbol_C])

    def test_add_new_rule_when_rule_effective(self):
        grammar = Grammar()
        self.covering.produce_rule = MagicMock(return_value=self.rule_1)
        self.covering.rule_is_effective = MagicMock(return_value=False)
        self.covering.make_rule_effective = MagicMock()
        self.covering.crowding.add_rule = MagicMock()

        result = self.covering.add_new_rule(grammar, self.symbol_A)

        self.assertEqual(self.rule_1, result)
        self.covering.rule_is_effective.assert_called_once_with(grammar, self.rule_1.left)
        self.covering.make_rule_effective.assert_called_once_with(grammar, self.rule_1)
        self.covering.crowding.add_rule.assert_not_called()

    def test_add_new_rule_when_rule_ineffective(self):
        grammar = Grammar()
        self.covering.produce_rule = MagicMock(return_value=self.rule_1)
        self.covering.rule_is_effective = MagicMock(return_value=True)
        self.covering.make_rule_effective = MagicMock()
        self.covering.crowding.add_rule = MagicMock()

        result = self.covering.add_new_rule(grammar, self.symbol_A, self.symbol_B)

        self.assertEqual(self.rule_1, result)
        self.covering.rule_is_effective.assert_called_once_with(grammar, self.rule_1.left)
        self.covering.make_rule_effective.assert_not_called()
        self.covering.crowding.add_rule.assert_called_once_with(grammar, self.rule_1)
