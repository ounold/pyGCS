from unittest import TestCase
from unittest.mock import MagicMock

from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.domain.types.SymobolType import SymbolType
from modules.GCSBase.grammar.grammar import Grammar
from modules.Heuristic.SplitAndMerge.split_and_merge import SplitAndMerge
from modules.sGCS.domain.sRule import sRule


class TestSplitAndMerge(TestCase):

    def setUp(self):
        settings = MagicMock()
        settings.get_value = MagicMock(side_effect=["TERMINALS", 0.5, 1.0, 1.0, 1.0, 1.0])
        self.grammar = Grammar(settings)

        self.symbol_a = Symbol('a', SymbolType.ST_TERMINAL)

        self.symbol_S = Symbol('S', SymbolType.ST_NON_TERMINAL)
        self.symbol_A = Symbol('A', SymbolType.ST_NON_TERMINAL)
        self.symbol_B = Symbol('B', SymbolType.ST_NON_TERMINAL)
        self.symbol_C = Symbol('A', SymbolType.ST_NON_TERMINAL)
        self.symbol_A1 = Symbol('A1', SymbolType.ST_NON_TERMINAL)
        self.symbol_A2 = Symbol('A2', SymbolType.ST_NON_TERMINAL)

        self.rule_1 = sRule.from_symbols(0.1, self.symbol_S, self.symbol_A, self.symbol_B)
        self.rule_2 = sRule.from_symbols(0.5, self.symbol_A, self.symbol_A, self.symbol_B)
        self.rule_3 = sRule.from_symbols(0.4, self.symbol_A, self.symbol_a)
        self.rule_4 = sRule.from_symbols(0.9, self.symbol_B, self.symbol_B, self.symbol_B)
        self.rule_5 = sRule.from_symbols(0.2, self.symbol_B, self.symbol_a)

        self.rules = {self.rule_1, self.rule_2, self.rule_3, self.rule_4, self.rule_5}
        self.non_terminal_rules = {self.rule_1, self.rule_2, self.rule_4}
        self.terminal_rules = {self.rule_3, self.rule_5}
        self.grammar.rulesContainer.terminal_rules = self.terminal_rules
        self.grammar.rulesContainer.non_terminal_rules = self.non_terminal_rules
        self.grammar.rulesContainer.rules = self.rules

        self.grammar.get_rules = MagicMock(return_value=self.rules)
        self.grammar.get_non_terminal_rules = MagicMock(return_value=self.non_terminal_rules)

        settings.get_value = MagicMock(side_effect=['RANDOM', 'False', 0.5, 20])
        self.split_and_merge = SplitAndMerge(settings)
        self.split_and_merge.iteration.add_rule = MagicMock()
        self.split_and_merge.iteration.remove_crowding_rule = MagicMock()

        self.merge_result = {
            sRule.from_symbols(0.1, self.symbol_S, self.symbol_A, self.symbol_A),
            sRule.from_symbols(0.1, self.symbol_A, self.symbol_A, self.symbol_A),
            sRule.from_symbols(0.1, self.symbol_A, self.symbol_a)
        }

        self.split_result = {
            sRule.from_symbols(0.1, self.symbol_S, self.symbol_A1, self.symbol_B),
            sRule.from_symbols(0.1, self.symbol_S, self.symbol_A2, self.symbol_B),
            sRule.from_symbols(0.1, self.symbol_A1, self.symbol_A1, self.symbol_B),
            sRule.from_symbols(0.1, self.symbol_A1, self.symbol_A2, self.symbol_B),
            sRule.from_symbols(0.1, self.symbol_A2, self.symbol_A2, self.symbol_B),
            sRule.from_symbols(0.1, self.symbol_A2, self.symbol_A1, self.symbol_B),
            sRule.from_symbols(0.1, self.symbol_A1, self.symbol_a),
            sRule.from_symbols(0.1, self.symbol_A2, self.symbol_a),
            sRule.from_symbols(0.1, self.symbol_B, self.symbol_a),
            sRule.from_symbols(0.1, self.symbol_B, self.symbol_B, self.symbol_B),

        }

    def test_merge(self):
        self.split_and_merge._SplitAndMerge__get_random_nonterminals_pair = MagicMock(
            return_value=(self.symbol_A, self.symbol_B))
        self.split_and_merge.merge(self.grammar)
        self.assertEqual(self.grammar.get_rules(), self.merge_result)

    def test_split(self):
        self.split_and_merge._SplitAndMerge__get_random_nonterminal = MagicMock(
            return_value=self.symbol_A)
        self.split_and_merge._SplitAndMerge__find_unused_symbols_pair = MagicMock(
            return_value=(self.symbol_A1, self.symbol_A2))
        self.split_and_merge.split(self.grammar)
        self.assertEqual(self.grammar.get_rules(), self.split_result)
