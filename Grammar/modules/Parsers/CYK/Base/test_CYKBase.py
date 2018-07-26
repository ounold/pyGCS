from unittest import TestCase

from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.Parsers.CYK.Base.CYKBase import CYKBase


class TestCYKBase(TestCase):
    def setUp(self):
        self.cyk_base = CYKBase(self.__create_test_grammar(), 0, None)

    def test_init_probability_array(self):
        test_sentence = "aaabbb"
        self.cyk_base._init_probability_array(len(test_sentence), len(self.cyk_base.grammar.nonTerminalSymbols))
        self.assertEqual(len(self.cyk_base.probability_array), 6)
        self.assertEqual(len(self.cyk_base.probability_array[0]), 6)
        self.assertEqual(len(self.cyk_base.probability_array[0][0]), 6)

    def test_init_probability_array_2(self):
        test_sentence = "aaa"
        self.cyk_base._init_probability_array(len(test_sentence), len(self.cyk_base.grammar.nonTerminalSymbols))
        self.assertEqual(len(self.cyk_base.probability_array), 3)
        self.assertEqual(len(self.cyk_base.probability_array[0]), 3)
        self.assertEqual(len(self.cyk_base.probability_array[0][0]), 6)

    def test_init_probability_array_3(self):
        test_sentence = "a"
        self.cyk_base._init_probability_array(len(test_sentence), len(self.cyk_base.grammar.nonTerminalSymbols))
        self.assertEqual(len(self.cyk_base.probability_array), 1)
        self.assertEqual(len(self.cyk_base.probability_array[0]), 1)
        self.assertEqual(len(self.cyk_base.probability_array[0][0]), 6)

    def test_init_probability_array_4(self):
        test_sentence = ""
        self.cyk_base._init_probability_array(len(test_sentence), len(self.cyk_base.grammar.nonTerminalSymbols))
        self.assertEqual(len(self.cyk_base.probability_array), 0)

    def test_init_probability_array_default_value_filling(self):
        test_sentence = "aaabbb"
        default_value = 0
        self.cyk_base.default_value = default_value
        self.cyk_base._init_probability_array(len(test_sentence), len(self.cyk_base.grammar.nonTerminalSymbols))
        probability_array = self.cyk_base.probability_array
        for i in range(len(test_sentence)):
            for j in range(len(test_sentence)):
                for k in range(len(self.cyk_base.grammar.nonTerminalSymbols)):
                    self.assertEqual(probability_array[i][j][k], default_value)

    def test_init_probability_array_default_value_filling_2(self):
        test_sentence = "aaabbb"
        default_value = None
        self.cyk_base.default_value = default_value
        self.cyk_base._init_probability_array(len(test_sentence), len(self.cyk_base.grammar.nonTerminalSymbols))
        probability_array = self.cyk_base.probability_array
        for i in range(len(test_sentence)):
            for j in range(len(test_sentence)):
                for k in range(len(self.cyk_base.grammar.nonTerminalSymbols)):
                    self.assertEqual(probability_array[i][j][k], default_value)

    def test_init_rules_table(self):
        test_sentence = "aaabbb"
        self.cyk_base._init_rules_table(len(test_sentence))
        self.assertEqual(len(self.cyk_base.rules_table), len(test_sentence))
        self.assertEqual(len(self.cyk_base.rules_table[0]), len(test_sentence))

    def test_init_rules_table_2(self):
        test_sentence = "aaa"
        self.cyk_base._init_rules_table(len(test_sentence))
        self.assertEqual(len(self.cyk_base.rules_table), len(test_sentence))
        self.assertEqual(len(self.cyk_base.rules_table[0]), len(test_sentence))

    def test_init_symbol_sequence(self):
        test_sentence = "aaabbbb"
        non_terminal_symbols = self.cyk_base.grammar.nonTerminalSymbols
        self.cyk_base._init_symbol_sequence(test_sentence)
        sequence = self.cyk_base.sequence
        self.assertEqual(sequence[0], non_terminal_symbols[0])
        self.assertEqual(sequence[1], non_terminal_symbols[0])
        self.assertEqual(sequence[2], non_terminal_symbols[0])
        self.assertEqual(sequence[3], non_terminal_symbols[1])
        self.assertEqual(sequence[4], non_terminal_symbols[1])
        self.assertEqual(sequence[5], non_terminal_symbols[1])

    def test_init_symbol_sequence_2(self):
        test_sentence = "acabef"
        non_terminal_symbols = self.cyk_base.grammar.nonTerminalSymbols
        self.cyk_base._init_symbol_sequence(test_sentence)
        sequence = self.cyk_base.sequence
        self.assertEqual(sequence[0], non_terminal_symbols[0])
        self.assertEqual(sequence[1], non_terminal_symbols[2])
        self.assertEqual(sequence[2], non_terminal_symbols[0])
        self.assertEqual(sequence[3], non_terminal_symbols[1])
        self.assertEqual(sequence[4], non_terminal_symbols[4])
        self.assertEqual(sequence[5], non_terminal_symbols[5])

    def test_init_symbol_sequence_unknown_ending_symbol(self):
        test_sentence = "acabex"
        non_terminal_symbols = self.cyk_base.grammar.nonTerminalSymbols
        self.cyk_base._init_symbol_sequence(test_sentence)
        sequence = self.cyk_base.sequence
        self.assertEqual(sequence[0], non_terminal_symbols[0])
        self.assertEqual(sequence[1], non_terminal_symbols[2])
        self.assertEqual(sequence[2], non_terminal_symbols[0])
        self.assertEqual(sequence[3], non_terminal_symbols[1])
        self.assertEqual(sequence[4], non_terminal_symbols[4])
        self.assertEqual(sequence[5], None)

    def __create_test_grammar(self):
        grammar: Grammar = Grammar()
        grammar.nonTerminalSymbols = self.__create_non_terminal_symbols()
        return grammar

    def __create_non_terminal_symbols(self):
        return [
            Symbol('a', SymbolType.ST_NON_TERMINAL),
            Symbol('b', SymbolType.ST_NON_TERMINAL),
            Symbol('c', SymbolType.ST_NON_TERMINAL),
            Symbol('d', SymbolType.ST_NON_TERMINAL),
            Symbol('e', SymbolType.ST_NON_TERMINAL),
            Symbol('f', SymbolType.ST_NON_TERMINAL),
        ]
