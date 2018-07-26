import random
from unittest import TestCase
from unittest.mock import MagicMock

from modules.Covering.SmartCovering.aggressive_smart_covering import RouletteSelection
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType


class Test_RouletteSelection(TestCase):

    def setUp(self):
        self.roulette_selection = RouletteSelection()
        self.symbol_a = Symbol('a', SymbolType.ST_TERMINAL)
        self.symbol_b = Symbol('b', SymbolType.ST_TERMINAL)
        self.symbol_c = Symbol('c', SymbolType.ST_TERMINAL)
        self.symbol_d = Symbol('d', SymbolType.ST_TERMINAL)
        self.symbol_e = Symbol('e', SymbolType.ST_TERMINAL)
        self.wheel_sections = [45, 30, 18, 9, 3]
        self.symbol_statistics = [(self.symbol_a, 15), (self.symbol_b, 12), (self.symbol_c, 9), (self.symbol_d, 6),
                                  (self.symbol_e, 3)]

    def test_sum_values(self):
        result = self.roulette_selection.sum_values(self.symbol_statistics)
        self.assertEqual(result, 45)

    def test_count_sections_of_roulette_wheel(self):
        result = self.roulette_selection.count_sections_of_roulette_wheel(self.symbol_statistics)
        expected = self.wheel_sections
        self.assertEqual(result, expected)

    def test_find_symbol(self):
        result = self.roulette_selection.find_symbol(self.symbol_statistics, self.wheel_sections, 20)
        self.assertEqual(result, self.symbol_b)

        result = self.roulette_selection.find_symbol(self.symbol_statistics, self.wheel_sections, 5)
        self.assertEqual(result, self.symbol_d)

        result = self.roulette_selection.find_symbol(self.symbol_statistics, self.wheel_sections, 0)
        self.assertEqual(result, self.symbol_e)

        result = self.roulette_selection.find_symbol(self.symbol_statistics, self.wheel_sections, 45)
        self.assertEqual(result, self.symbol_a)

    def test_select(self):
        random.randint = MagicMock(return_value=20)
        result = self.roulette_selection.select(self.symbol_statistics)
        self.assertEqual(result, self.symbol_b)

        random.randint = MagicMock(return_value=5)
        result = self.roulette_selection.select(self.symbol_statistics)
        self.assertEqual(result, self.symbol_d)

        random.randint = MagicMock(return_value=0)
        result = self.roulette_selection.select(self.symbol_statistics)
        self.assertEqual(result, self.symbol_e)

        random.randint = MagicMock(return_value=45)
        result = self.roulette_selection.select(self.symbol_statistics)
        self.assertEqual(result, self.symbol_a)
