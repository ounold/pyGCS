import unittest

from modules.GCSBase.domain.symbol import Symbol, SymbolType
from modules.GCSBase.utils.symbol_utils import SymbolFinder


class TestSymbolFinder(unittest.TestCase):

    def setUp(self):
        self.symbols = [Symbol("A", SymbolType.ST_TERMINAL),
                        Symbol("B", SymbolType.ST_UNIVERSAL),
                        Symbol("C", SymbolType.ST_NON_TERMINAL),
                        Symbol("D", SymbolType.ST_START)]

    def test_find_symbol_by_char(self):
        symbol = Symbol("B", SymbolType.ST_UNIVERSAL)
        found_symbol = SymbolFinder.find_symbol_by_char(self.symbols, symbol.value)
        self.assertEqual(found_symbol, symbol)

    def test_symbol_not_found(self):
        value = "e"
        found_symbol = SymbolFinder.find_symbol_by_char(self.symbols, value)
        self.assertIsNone(found_symbol)

    def test_string_to_symbols_parsing(self):
        rule_string = "A->BC P=0.4"
        symbols = SymbolFinder.symbols_from_parsed_rule(rule_string, self.symbols)
        self.assertEqual(len(symbols), 3)
        self.assertEqual(symbols[0], self.symbols[0])
        self.assertEqual(symbols[1], self.symbols[1])
        self.assertEqual(symbols[2], self.symbols[2])

    def test_string_to_symbols_parsing_one_right(self):
        rule_string = "A->B P=0.4"
        symbols = SymbolFinder.symbols_from_parsed_rule(rule_string, self.symbols)
        self.assertEqual(len(symbols), 2)
        self.assertEqual(symbols[0], self.symbols[0])
        self.assertEqual(symbols[1], self.symbols[1])

