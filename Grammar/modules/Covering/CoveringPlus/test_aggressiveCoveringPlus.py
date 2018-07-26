from unittest import TestCase
from unittest.mock import MagicMock

from modules.Covering.CoveringPlus.aggressive_covering_plus import AggressiveCoveringPlus
from modules.Crowding.crowding import Crowding
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Visualisation.iteration import Iteration
from modules.sGCS.domain.sRule import sRule


class TestAggressiveCoveringPlus(TestCase):

    def setUp(self):
        iteration = Iteration()
        self.crowding = Crowding()
        self.crowding.set_iteration(iteration)
        self.covering = AggressiveCoveringPlus(self.crowding)
        self.covering.set_iteration(iteration)
        self.grammar = Grammar()
        self.first_right_symbol = Symbol('a', SymbolType.ST_TERMINAL)
        self.second_right_symbol = Symbol('b', SymbolType.ST_TERMINAL)
        self.left_symbol = Symbol('x', SymbolType.ST_TERMINAL)
        self.rule = sRule.from_symbols(0.5, self.left_symbol, self.first_right_symbol, self.second_right_symbol)

    def test_add_new_rule(self):
        self.crowding.add_rule = MagicMock()
        self.covering.produce_rule = MagicMock(return_value=self.rule)
        result = self.covering.add_new_rule(self.grammar, self.left_symbol, self.first_right_symbol)

        self.crowding.add_rule.assert_called_once()
        self.assertEqual(result, self.rule)

    def test_produce_rule(self):
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock(return_value=self.left_symbol)
        RandomUtils.get_random_probability = MagicMock(return_value=0.5)

        result = self.covering.produce_rule(self.grammar, self.first_right_symbol, self.second_right_symbol)
        expected = self.rule
        self.assertEqual(result, expected)
