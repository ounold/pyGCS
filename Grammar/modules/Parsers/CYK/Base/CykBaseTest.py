import unittest

from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.grammar.grammar import Grammar

from .CYKBase import CYKBase


class CykBaseTest(unittest.TestCase):

    def setUp(self):
        self.cyk_base = CYKBase(0)

    def test_table_init(self):
        sentence = "I like sunny weather"
        non_teminals = [0 for i in range(5)]
        self.cyk_base._init_rules_table(sentence, non_teminals)
        self.assertEqual(len(sentence), len(self.cyk_base.probability_array))
        self.assertEqual(len(sentence), len(self.cyk_base.probability_array[0]))
        self.assertEqual(len(non_teminals), len(self.cyk_base.probability_array[0][0]))

    def test_table_init_2(self):
        sentence = "I like sunny weather and snowy too"
        non_terminals = [0 for i in range(10)]
        self.cyk_base._init_rules_table(sentence, non_terminals)
        self.assertEqual(len(sentence), len(self.cyk_base.probability_array))
        self.assertEqual(len(sentence), len(self.cyk_base.probability_array[0]))
        self.assertEqual(len(non_terminals), len(self.cyk_base.probability_array[0][0]))

    def test_table_init_default_values(self):
        sentence = "I like sunny weather"
        non_terminals = [0 for i in range(5)]
        default_value = 0
        self.cyk_base._init_rules_table(sentence, non_terminals)
        for i in range(len(sentence)):
            for j in range(len(sentence)):
                for k in range(len(non_terminals)):
                    self.assertEqual(default_value, self.cyk_base.probability_array[i][j][k])

    def test_table_init_default_values_custom(self):
        self.cyk_base = CYKBase("A")
        sentence = "I like sunny weather"
        non_terminals = [0 for i in range(5)]
        default_value = "A"
        self.cyk_base._init_rules_table(sentence, non_terminals)
        for i in range(len(sentence)):
            for j in range(len(sentence)):
                for k in range(len(non_terminals)):
                    self.assertEqual(default_value, self.cyk_base.probability_array[i][j][k])

    def test_symbol_sentence_init(self):
        symbol1 = Symbol("I")
        symbol2 = Symbol(" ")
        symbol3 = Symbol("l")
        symbol4 = Symbol("i")
        symbol5 = Symbol("k")
        symbol6 = Symbol("e")

        symbols = [symbol1, symbol2, symbol3, symbol4, symbol5, symbol6]
        sentence = "I like you"

        grammar = Grammar()
        grammar.nonTerminalSymbols = symbols
        self.cyk_base = CYKBase()
        self.cyk_base.grammar = grammar
        self.cyk_base.symbols = symbols
        self.cyk_base._init_symbol_sequence(sentence)

        sequence = self.cyk_base.sequence
        self.assertEqual(symbol1, sequence[0])
        self.assertEqual(symbol2, sequence[1])
        self.assertEqual(symbol3, sequence[2])
        self.assertEqual(symbol4, sequence[3])
        self.assertEqual(symbol5, sequence[4])
        self.assertEqual(symbol6, sequence[5])
        self.assertEqual(symbol2, sequence[6])
        self.assertEqual(None, sequence[7])
        self.assertEqual(None, sequence[8])
        self.assertEqual(None, sequence[9])
        pass

    def test_symbol_sentence_init_2(self):
        symbol1 = Symbol("I")
        symbol2 = Symbol(" ")
        symbol3 = Symbol("l")
        symbol4 = Symbol("i")
        symbol5 = Symbol("k")
        symbol6 = Symbol("e")

        symbols = [symbol1, symbol2, symbol3, symbol4, symbol5, symbol6]
        sentence = "I do not like you"

        grammar = Grammar()
        grammar.nonTerminalSymbols = symbols
        self.cyk_base = CYKBase()
        self.cyk_base.grammar = grammar
        self.cyk_base.symbols = symbols
        self.cyk_base._init_symbol_sequence(sentence)

        sequence = self.cyk_base.sequence
        self.assertEqual(symbol1, sequence[0])
        self.assertEqual(symbol2, sequence[1])
        self.assertEqual(None, sequence[2])
        self.assertEqual(None, sequence[3])
        self.assertEqual(symbol2, sequence[4])
        self.assertEqual(None, sequence[5])
        self.assertEqual(None, sequence[6])
        self.assertEqual(None, sequence[7])
        self.assertEqual(symbol2, sequence[8])
        self.assertEqual(symbol3, sequence[9])
        self.assertEqual(symbol4, sequence[10])
        self.assertEqual(symbol5, sequence[11])
        self.assertEqual(symbol6, sequence[12])
        self.assertEqual(symbol2, sequence[13])
        self.assertEqual(None, sequence[14])
        self.assertEqual(None, sequence[15])
        self.assertEqual(None, sequence[16])

