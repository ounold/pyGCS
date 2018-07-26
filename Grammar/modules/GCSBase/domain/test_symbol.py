import unittest

from modules.GCSBase.domain.symbol import Symbol, SymbolType


class TestSymbol(unittest.TestCase):
    def setUp(self):
        self.symbol = Symbol()

    def test_is_terminal(self):
        self.symbol.symbol_type = SymbolType.ST_TERMINAL
        self.assertTrue(self.symbol.is_terminal())

    def test_is_terminal_failure(self):
        self.symbol.symbol_type = SymbolType.ST_UNIVERSAL
        self.assertFalse(self.symbol.is_terminal())

    def test_is_non_terminal(self):
        self.symbol.symbol_type = SymbolType.ST_NON_TERMINAL
        self.assertTrue(self.symbol.is_non_terminal())

    def test_is_non_terminal_failure(self):
        self.symbol.symbol_type = SymbolType.ST_TERMINAL
        self.assertFalse(self.symbol.is_non_terminal())

    def test_is_start(self):
        self.symbol.symbol_type = SymbolType.ST_START
        self.assertTrue(self.symbol.is_start())

    def test_is_start_failure(self):
        self.symbol.symbol_type = SymbolType.ST_TERMINAL
        self.assertFalse(self.symbol.is_start())

    def test_is_universal(self):
        self.symbol.symbol_type = SymbolType.ST_UNIVERSAL
        self.assertTrue(self.symbol.is_universal())

    def test_is_universal_failure(self):
        self.symbol.symbol_type = SymbolType.ST_TERMINAL
        self.assertFalse(self.symbol.is_universal())

    def test_two_symbols_equality(self):
        self.symbol.symbol_type = SymbolType.ST_TERMINAL
        self.symbol.value = "a"
        other_symbol = Symbol("a", SymbolType.ST_TERMINAL)
        self.assertEqual(self.symbol, other_symbol)

    def test_two_symbols_not_equal(self):
        self.symbol.symbol_type = SymbolType.ST_TERMINAL
        self.symbol.value = "a"
        other_symbol = Symbol("c", SymbolType.ST_UNIVERSAL)
        self.assertNotEqual(self.symbol, other_symbol)

    def test_two_symbols_not_equal_different_types(self):
        self.symbol.symbol_type = SymbolType.ST_TERMINAL
        self.symbol.value = "a"
        other_symbol = Symbol("a", SymbolType.ST_NON_TERMINAL)
        self.assertNotEqual(self.symbol, other_symbol)

    def test_two_symbols_not_equal_different_values(self):
        self.symbol.symbol_type = SymbolType.ST_TERMINAL
        self.symbol.value = "a"
        other_symbol = Symbol("b", SymbolType.ST_TERMINAL)
        self.assertNotEqual(self.symbol, other_symbol)

    def test_conversion_to_string(self):
        self.symbol.symbol_type = SymbolType.ST_TERMINAL
        self.symbol.value = "a"
        self.assertEqual(str(self.symbol), "a")
