import random
from unittest import TestCase
from unittest.mock import MagicMock

from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.random_utils import RandomUtils


class TestRandomUtils(TestCase):

    def test_get_random_nonterminal_symbol_from(self):
        grammar = Grammar()
        symbol_1 = Symbol('a', SymbolType.ST_TERMINAL)
        symbol_2 = Symbol('b', SymbolType.ST_TERMINAL)

        grammar.nonTerminalSymbols = [symbol_1, symbol_2]
        result = RandomUtils.get_random_nonterminal_symbol_from(grammar)
        self.assertIsNotNone(result)
        self.assertEqual(2, len(grammar.nonTerminalSymbols))

        grammar.nonTerminalSymbols = []
        result = RandomUtils.get_random_nonterminal_symbol_from(grammar)
        self.assertIsNone(result)

        grammar.nonTerminalSymbols = [symbol_1, symbol_2]
        random.choice = MagicMock(return_value=symbol_1)
        result = RandomUtils.get_random_nonterminal_symbol_from(grammar)
        self.assertEqual(result, symbol_1)

    def test_get_random_probability(self):
        result = RandomUtils.get_random_probability()
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 1)

    def test_make_random_decision_with_probability(self):
        random.random = MagicMock(return_value=0.5)
        result = RandomUtils.make_random_decision_with_probability(0.7)
        self.assertTrue(result)

        random.random = MagicMock(return_value=0.9)
        result = RandomUtils.make_random_decision_with_probability(0.7)
        self.assertFalse(result)

