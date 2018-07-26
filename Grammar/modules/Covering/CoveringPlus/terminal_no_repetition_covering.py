import random

from modules.GCSBase.domain.Rule import RuleOrigin
from settings.settings import Settings
from ..Covering import Covering
from ...GCSBase.domain import Rule
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils
from ...sGCS.domain.sRule import sRuleBuilder


class TerminalNoRepetitionCovering(Covering):

    def __init__(self, settings: Settings):
        self.non_terminal_symbols = int(settings.get_value('general', 'non_terminal_symbols_number_for_terminal_covering'))
        super().__init__()

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        new_rule = self.produce_rule(grammar, first_symbol)
        grammar.add_rule(new_rule)
        self.iteration.add_covering_rule(new_rule)
        self.log_rule(new_rule)
        return new_rule

    def produce_rule(self, grammar: Grammar, right_symbol: Symbol) -> Rule:
        random_left_symbol = self.find_left_symbol(grammar)
        probability = RandomUtils.get_random_probability()
        return sRuleBuilder() \
            .left_symbol(random_left_symbol) \
            .first_right_symbol(right_symbol) \
            .probability(probability) \
            .origin(RuleOrigin.COVERING) \
            .create()

    def find_left_symbol(self, grammar):
        non_terminal_symbols_in_use = set(map(lambda rule: rule.left, grammar.get_terminal_rules()))
        if len(non_terminal_symbols_in_use) >= self.non_terminal_symbols:
            return random.sample(non_terminal_symbols_in_use, 1)[0]

        all_non_terminal_symbols = set(grammar.nonTerminalSymbols)
        available_symbols = all_non_terminal_symbols - non_terminal_symbols_in_use
        if len(available_symbols) > 0:
            return random.sample(available_symbols, 1)[0]
        else:
            return RandomUtils.get_random_nonterminal_symbol_from(grammar)
