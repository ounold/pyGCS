from unittest import TestCase

from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar


class GrammarTest(TestCase):
    def setUp(self):
        self.grammar = Grammar()
        self.grammar.terminalSymbols = self.__create_terminal_symbols__()
        self.grammar.nonTerminalSymbols = self.__create_non_terminal_symbols()

    def test_should_not_find_symbol_index(self):
        symbol = Symbol("d")
        symbol_idx = self.grammar.symbol_index(symbol)
        self.assertEqual(symbol_idx, -1)

    def test_should_find_first_terminal_symbol(self):
        symbol = Symbol("o")
        symbol_idx = self.grammar.symbol_index(symbol)
        self.assertEqual(symbol_idx, 0)

    def test_should_find_second_terminal_symbol(self):
        symbol = Symbol("t")
        symbol_idx = self.grammar.symbol_index(symbol)
        self.assertEqual(symbol_idx, 1)

    def test_should_find_third_terminal_symbol(self):
        symbol = Symbol("s")
        symbol_idx = self.grammar.symbol_index(symbol)
        self.assertEqual(symbol_idx, 2)

    def test_should_find_first_non_terminal_symbol(self):
        symbol = Symbol("a")
        symbol_idx = self.grammar.symbol_index(symbol)
        self.assertEqual(symbol_idx, 3)

    def test_should_find_second_non_terminal_symbol(self):
        symbol = Symbol("b")
        symbol_idx = self.grammar.symbol_index(symbol)
        self.assertEqual(symbol_idx, 4)

    def test_should_find_third_non_terminal_symbol(self):
        symbol = Symbol("c")
        symbol_idx = self.grammar.symbol_index(symbol)
        self.assertEqual(symbol_idx, 5)

    def test_should_find_symbol_by_index(self):
        index = 0
        symbol = self.grammar.find_symbol_by_given_index(index)
        self.assertEqual(symbol, Symbol("o", SymbolType.ST_TERMINAL))

    def test_should_find_symbol_by_index_1(self):
        index = 1
        symbol = self.grammar.find_symbol_by_given_index(index)
        self.assertEqual(symbol, Symbol("t", SymbolType.ST_TERMINAL))

    def test_should_find_symbol_by_index_5(self):
        index = 5
        symbol = self.grammar.find_symbol_by_given_index(index)
        self.assertEqual(symbol, Symbol("c", SymbolType.ST_NON_TERMINAL))

    def test_should_not_find_symbol(self):
        index = -1
        index2 = 100000000000
        symbol = self.grammar.find_symbol_by_given_index(index)
        symbol2 = self.grammar.find_symbol_by_given_index(index2)
        self.assertEqual(symbol, None)
        self.assertEqual(symbol2, None)

    def test_should_find_non_terminal_symbol_index(self):
        symbol = Symbol("a", SymbolType.ST_NON_TERMINAL)
        index = self.grammar.find_non_terminal_symbol_index(symbol)
        self.assertEqual(index, 0)

    def test_should_find_non_terminal_symbol_index_2(self):
        symbol = Symbol("b", SymbolType.ST_NON_TERMINAL)
        index = self.grammar.find_non_terminal_symbol_index(symbol)
        self.assertEqual(index, 1)

    def test_should_find_non_terminal_symbol_index_3(self):
        symbol = Symbol("c", SymbolType.ST_NON_TERMINAL)
        index = self.grammar.find_non_terminal_symbol_index(symbol)
        self.assertEqual(index, 2)

    def test_should_not_find_non_terminal_symbol_index(self):
        symbol = Symbol("d", SymbolType.ST_NON_TERMINAL)
        index = self.grammar.find_non_terminal_symbol_index(symbol)
        self.assertEqual(index, -1)

    def test_find_symbol_by_value(self):
        value = 'c'
        symbol = self.grammar.find_symbol_by_value(value)
        self.assertEqual(symbol, Symbol("c", SymbolType.ST_NON_TERMINAL))

    def test_should_not_find_symbol_by_value(self):
        value = 'z'
        symbol = self.grammar.find_symbol_by_value(value)
        self.assertEqual(symbol, None)

    def test_should_calculate_grammar_fitness(self):
        self.grammar.trueNegative = 3
        self.grammar.truePositive = 5
        all_examples = 8
        fitness = self.grammar.calculate_grammar_fitness(all_examples)
        self.assertEqual(fitness, 1)

    def test_should_calculate_grammar_fitness_2(self):
        self.grammar.trueNegative = 3
        self.grammar.truePositive = 5
        all_examples = 16
        fitness = self.grammar.calculate_grammar_fitness(all_examples)
        self.assertEqual(fitness, 0.5)

    def test_should_calculate_grammar_fitness_3(self):
        self.grammar.trueNegative = 3
        self.grammar.truePositive = 5
        all_examples = 32
        fitness = self.grammar.calculate_grammar_fitness(all_examples)
        self.assertEqual(fitness, 0.25)

    def test_should_calculate_grammar_fitness_4(self):
        self.grammar.trueNegative = 3
        self.grammar.truePositive = 5
        all_examples = 64
        fitness = self.grammar.calculate_grammar_fitness(all_examples)
        self.assertEqual(fitness, 0.125)

    def test_should_calculate_grammar_fitness_no_examples(self):
        all_examples = 0
        fitness = self.grammar.calculate_grammar_fitness(all_examples)
        self.assertEqual(fitness, 0)

    def test_should_calculate_grammar_sensitivity_no_positive_and_negative(self):
        sensitivity = self.grammar.calculate_sensitivity()
        self.assertEqual(sensitivity, 0)

    def test_should_calculate_grammar_sensitivity(self):
        self.grammar.falseNegative = 3
        self.grammar.truePositive = 5
        sensitivity = self.grammar.calculate_sensitivity()
        self.assertEqual(sensitivity, 0.625)

    def test_should_calculate_grammar_sensitivity_2(self):
        self.grammar.falseNegative = 4
        self.grammar.truePositive = 4
        sensitivity = self.grammar.calculate_sensitivity()
        self.assertEqual(sensitivity, 0.5)

    def test_should_calculate_grammar_sensitivity_3(self):
        self.grammar.falseNegative = 9
        self.grammar.truePositive = 1
        sensitivity = self.grammar.calculate_sensitivity()
        self.assertEqual(sensitivity, 0.1)

    def test_should_calculate_precision_no_positives(self):
        precision = self.grammar.calculate_precision()
        self.assertEqual(precision, 0)

    def test_should_calculate_precision(self):
        self.grammar.truePositive = 2
        self.grammar.falsePositive = 8
        precision = self.grammar.calculate_precision()
        self.assertEqual(precision, 0.2)

    def test_should_calculate_precision_2(self):
        self.grammar.truePositive = 1
        self.grammar.falsePositive = 7
        precision = self.grammar.calculate_precision()
        self.assertEqual(precision, 0.125)

    def test_should_calculate_precision_3(self):
        self.grammar.truePositive = 3
        self.grammar.falsePositive = 5
        precision = self.grammar.calculate_precision()
        self.assertEqual(precision, 0.375)

    def test_should_calculate_precision_4(self):
        self.grammar.truePositive = 3
        self.grammar.falsePositive = 0
        precision = self.grammar.calculate_precision()
        self.assertEqual(precision, 1.00)

    def test_should_calculate_specificity_no_data(self):
        specificity = self.grammar.calculate_specificity()
        self.assertEqual(specificity, 0)

    def test_should_calculate_specificity(self):
        self.grammar.trueNegative = 3
        self.grammar.falsePositive = 7
        specificity = self.grammar.calculate_specificity()
        self.assertEqual(specificity, 0.3)

    def test_should_calculate_specificity_2(self):
        self.grammar.trueNegative = 1
        self.grammar.falsePositive = 9
        specificity = self.grammar.calculate_specificity()
        self.assertEqual(specificity, 0.1)

    def test_should_calculate_specificity_3(self):
        self.grammar.trueNegative = 0
        self.grammar.falsePositive = 10
        specificity = self.grammar.calculate_specificity()
        self.assertEqual(specificity, 0)

    def test_should_calculate_specificity_4(self):
        self.grammar.trueNegative = 10
        self.grammar.falsePositive = 0
        specificity = self.grammar.calculate_specificity()
        self.assertEqual(specificity, 1.0)

    def test_should_calculate_specificity_5(self):
        self.grammar.trueNegative = 3
        self.grammar.falsePositive = 5
        specificity = self.grammar.calculate_specificity()
        self.assertEqual(specificity, 0.375)

    def test_should_calculate_f1(self):
        self.grammar.truePositive = 2
        self.grammar.falseNegative = 2
        self.grammar.falsePositive = 2
        f1 = self.grammar.calculate_f1()
        self.assertEqual(f1, 0.5)

    def test_should_calculate_f1_2(self):
        self.grammar.truePositive = 2
        self.grammar.falseNegative = 4
        self.grammar.falsePositive = 4
        f1 = self.grammar.calculate_f1()
        self.assertEqual(f1, 1 / 3)

    def test_grammar_should_be_perfectly_fit(self):
        self.grammar.trueNegative = 2
        self.grammar.truePositive = 2
        all_examples = 4
        is_perfectly_fit = self.grammar.is_grammar_perfectly_fit(all_examples)
        self.assertTrue(is_perfectly_fit)

    def test_grammar_should_not_be_perfectly_fit(self):
        self.grammar.trueNegative = 2
        self.grammar.truePositive = 2
        all_examples = 5
        is_perfectly_fit = self.grammar.is_grammar_perfectly_fit(all_examples)
        self.assertFalse(is_perfectly_fit)

    def __create_terminal_symbols__(self):
        terminal_symbols = []
        symbol_one = Symbol("o", SymbolType.ST_TERMINAL)
        symbol_two = Symbol("t", SymbolType.ST_TERMINAL)
        symbol_three = Symbol("s", SymbolType.ST_TERMINAL)
        terminal_symbols.append(symbol_one)
        terminal_symbols.append(symbol_two)
        terminal_symbols.append(symbol_three)
        return terminal_symbols

    def __create_non_terminal_symbols(self):
        non_terminal_symbols = []
        symbol_one = Symbol("a", SymbolType.ST_NON_TERMINAL)
        symbol_two = Symbol("b", SymbolType.ST_NON_TERMINAL)
        symbol_three = Symbol("c", SymbolType.ST_NON_TERMINAL)
        non_terminal_symbols.append(symbol_one)
        non_terminal_symbols.append(symbol_two)
        non_terminal_symbols.append(symbol_three)
        return non_terminal_symbols
