from unittest import TestCase
from unittest.mock import MagicMock

from modules.Covering.StandardCovering.aggressive_standard_covering import AggressiveStandardCovering
from modules.Crowding.crowding import Crowding
from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Visualisation.iteration import Iteration


class TestAggressiveStandardCovering(TestCase):

    def setUp(self):
        iteration = Iteration()
        self.crowding = Crowding()
        self.crowding.set_iteration(iteration)
        self.covering = AggressiveStandardCovering(self.crowding)
        self.covering.set_iteration(iteration)
        self.grammar = Grammar()
        self.first_right_symbol = Symbol('a', SymbolType.ST_TERMINAL)
        self.second_right_symbol = Symbol('b', SymbolType.ST_TERMINAL)
        self.left_symbol = Symbol('x', SymbolType.ST_TERMINAL)
        self.rule = Rule([self.left_symbol, self.first_right_symbol, self.second_right_symbol])

    def test_add_new_rule(self):
        self.covering.crowding.add_rule = MagicMock()
        RandomUtils.get_random_nonterminal_symbol_from = MagicMock(return_value=self.left_symbol)

        result = self.covering.add_new_rule(self.grammar, self.first_right_symbol, self.second_right_symbol)

        self.assertEqual(self.rule, result)
        self.covering.crowding.add_rule.assert_called_once_with(self.grammar, self.rule)
        RandomUtils.get_random_nonterminal_symbol_from.assert_called_once_with(self.grammar)
