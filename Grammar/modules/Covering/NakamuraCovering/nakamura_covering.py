from typing import List

from ..Covering import Covering
from ...Crowding.crowding import Crowding
from ...GCSBase.domain.Rule import Rule, RuleOrigin
from ...GCSBase.domain.symbol import Symbol
from ...GCSBase.grammar.grammar import Grammar
from ...GCSBase.utils.random_utils import RandomUtils
from ...sGCS.domain.sRule import sRuleBuilder


class NakamuraCovering(Covering):

    def __init__(self, crowding: Crowding):
        super().__init__(crowding)

    def add_new_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        raise NotImplementedError

    def produce_rule(self, grammar: Grammar, first_symbol: Symbol, second_symbol: Symbol = None) -> Rule:
        random_left_symbol = RandomUtils.get_random_nonterminal_symbol_from(grammar)
        probability = RandomUtils.get_random_probability()
        return sRuleBuilder() \
            .left_symbol(random_left_symbol) \
            .first_right_symbol(first_symbol) \
            .second_right_symbol(second_symbol) \
            .probability(probability) \
            .origin(RuleOrigin.COVERING) \
            .create()

    def make_rule_effective(self, grammar: Grammar, rule: Rule):
        rules = [rule]
        current_symbol = rule.left

        while not self.rule_is_effective(grammar, current_symbol):
            new_rule = self.produce_rule_based_on_random_decision(grammar, current_symbol)
            rules.append(new_rule)
            self.crowding.add_rule(grammar, new_rule)
            self.iteration.add_covering_rule(new_rule)
            current_symbol = new_rule.left
        self.add_to_iteration(rules)
        self.crowding.add_rules(grammar, rules)

    def rule_is_effective(self, grammar: Grammar, left_symbol: Symbol):
        for rule in grammar.get_rules():
            if rule.right1 == left_symbol or rule.right2 == left_symbol:
                return True
        return False

    def produce_rule_based_on_random_decision(self, grammar: Grammar, current_symbol: Symbol) -> Rule:
        if RandomUtils.make_random_decision_with_probability(0.5):
            first_right_symbol = current_symbol
            second_right_symbol = RandomUtils.get_random_nonterminal_symbol_from(grammar)
        else:
            second_right_symbol = current_symbol
            first_right_symbol = RandomUtils.get_random_nonterminal_symbol_from(grammar)
        return self.produce_rule(grammar, first_right_symbol, second_right_symbol)

    def add_to_iteration(self, rules: List[Rule]) -> None:
        for rule in rules:
            self.iteration.add_covering_rule(rule)
