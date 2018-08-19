import random
from typing import List, Tuple, Set

from modules.Covering.NewCovering.new_covering import NewCovering
from modules.Covering.SmartCovering.aggressive_smart_covering import AggressiveSmartCovering
from modules.GCSBase.domain.Rule import Rule, RuleOrigin
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.grammar.grammar import Grammar
from modules.Heuristic.Heuristic import Heuristic
from modules.sGCS.domain.sRule import sRuleBuilder


class SplitAndMerge(Heuristic):

    def __init__(self, settings):
        super().__init__(settings=settings)
        self.__sm_symbol_selection_method = self.settings.get_value('general', 'sm_symbol_selection_method')
        self.__run_counter: int = 0
        self.__fitness_selection_method = NewCovering(settings=settings, crowding=None)
        self.__number_selection_method = AggressiveSmartCovering(crowding=None)

    def reset(self):
        super().reset()
        self.__run_counter = 0

    def run(self, grammar: Grammar) -> None:
        if self.__run_counter != 0:
            self.save_grammar_state(grammar)
            if len(grammar.get_non_terminal_rules()) > 2 * int(self.settings.get_value('general', 'non_terminal_productions_number')):
                self.merge(grammar)
            else:
                if self.__run_counter % 2 == 1:
                    self.split(grammar)
                else:
                    self.merge(grammar)
        self.__run_counter += 1

    def split(self, grammar: Grammar) -> None:
        replaced: Symbol = self.__find_nonterminal(grammar)
        replacement: Tuple[Symbol, Symbol] = self.__find_unused_symbols_pair(grammar)
        print("[split] replaced = {} replacement = {}".format(replaced, replacement))
        if replacement is not None:
            rules: Set[Rule] = grammar.get_rules()
            rules_copy = set(rules)
            for rule in rules_copy:
                if rule.left == replaced:
                    first_rule = self.__create_rule(replacement[0], rule.right1, rule.right2)
                    second_rule = self.__create_rule(replacement[1], rule.right1, rule.right2)
                    grammar.remove_rule(rule)
                    grammar.add_rule(first_rule)
                    grammar.add_rule(second_rule)
                    self.iteration.remove_crowding_rule(rule)
                    self.iteration.add_rule(first_rule)
                    self.iteration.add_rule(second_rule)

            rules: Set[Rule] = grammar.get_rules()
            rules_copy = set(rules)
            for rule in rules_copy:
                if rule.right1 == replaced:
                    grammar.remove_rule(rule)
                    first_rule = self.__create_rule(rule.left, replacement[0], rule.right2)
                    second_rule = self.__create_rule(rule.left, replacement[1], rule.right2)
                    grammar.add_rule(first_rule)
                    grammar.add_rule(second_rule)
                    self.iteration.remove_crowding_rule(rule)
                    self.iteration.add_rule(first_rule)
                    self.iteration.add_rule(second_rule)

            rules: Set[Rule] = grammar.get_rules()
            rules_copy = set(rules)
            for rule in rules_copy:
                if rule.right2 == replaced:
                    first_rule = self.__create_rule(rule.left, rule.right1, replacement[0])
                    second_rule = self.__create_rule(rule.left, rule.right1, replacement[1])
                    grammar.remove_rule(rule)
                    grammar.add_rule(first_rule)
                    grammar.add_rule(second_rule)
                    self.iteration.remove_crowding_rule(rule)
                    self.iteration.add_rule(first_rule)
                    self.iteration.add_rule(second_rule)

    def merge(self, grammar: Grammar) -> None:
        symbols: List[Symbol] = self.__get_nonterminals_pair(grammar)
        print("[merge] symbols = {}".format(symbols))
        if symbols is not None:
            self.__replace_all_symbols_in_rules(symbols[0], symbols[1], grammar)

    def __replace_all_symbols_in_rules(self, replacement: Symbol, replaced: Symbol, grammar: Grammar) -> None:
        rules: Set[Rule] = grammar.get_rules()
        rules_copy = set(rules)
        for rule in rules_copy:
            if self.__rule_contains_replaced_symbol(rule, replaced):
                new_rule = self.__replace_symbols_in_rule(replacement, replaced, rule)
                grammar.remove_rule(rule)
                grammar.add_rule(new_rule)

    def __replace_symbols_in_rule(self, replacement: Symbol, replaced: Symbol, rule: Rule) -> Rule:
        left = replacement if rule.left == replaced else rule.left
        right1 = replacement if rule.right1 == replaced else rule.right1
        right2 = replacement if rule.right2 == replaced else rule.right2
        return self.__create_rule(left, right1, right2)

    def __rule_contains_replaced_symbol(self, rule: Rule, replaced: Symbol) -> bool:
        return rule.left == replaced or rule.right1 == replaced or rule.right2 == replaced

    def __get_random_nonterminals_pair(self, grammar: Grammar) -> Tuple[Symbol, Symbol] or None:
        symbols_in_use = self.__get_non_terminals_in_use(grammar)
        try:
            return tuple(random.sample(symbols_in_use, 2))
        except ValueError:
            return None

    def __get_random_nonterminal(self, grammar: Grammar) -> Symbol or None:
        symbols_in_use = list(self.__get_non_terminals_in_use(grammar))
        try:
            return random.choice(symbols_in_use)
        except IndexError:
            return None

    def __find_unused_symbols_pair(self, grammar: Grammar) -> Tuple[Symbol, Symbol] or None:
        symbols_in_use = self.__get_non_terminals_in_use(grammar)
        all_symbols = set(grammar.nonTerminalSymbols)
        available_symbols = all_symbols.difference(symbols_in_use)
        if len(available_symbols) <= 1:
            return None
        else:
            return tuple(random.sample(available_symbols, 2))

    def __create_rule(self, left: Symbol, right1: Symbol, right2: Symbol) -> Rule:
        rule = sRuleBuilder() \
            .left_symbol(left) \
            .first_right_symbol(right1) \
            .second_right_symbol(right2) \
            .probability(0.0) \
            .origin(RuleOrigin.HEURISTIC) \
            .create()
        rule.age = 0
        return rule

    def __get_non_terminals_in_use(self, grammar: Grammar) -> Set[Symbol]:
        rules = grammar.get_rules()
        symbols_in_use = set()
        for rule in rules:
            symbols_in_use.add(rule.left)
            symbols_in_use.add(rule.right1)
            if rule.right2 is not None:
                symbols_in_use.add(rule.right2)
        return set(filter(lambda symbol: symbol.is_non_terminal(), symbols_in_use))

    def __find_nonterminal(self, grammar: Grammar) -> Symbol or None:
        # RANDOM, FITNESS, NUMBER
        if self.__sm_symbol_selection_method == 'FITNESS':
            the_best_rules = self.__fitness_selection_method.find_the_best_rules(grammar)
            return self.__fitness_selection_method.find_symbol_by_roulette_selection(the_best_rules)
        elif self.__sm_symbol_selection_method == 'NUMBER':
            return self.__number_selection_method.find_left_symbol_wisely(grammar)
        else:
            return self.__get_random_nonterminal(grammar)

    def __get_nonterminals_pair(self, grammar: Grammar) -> Tuple[Symbol, Symbol] or None:
        if self.__sm_symbol_selection_method == 'FITNESS' or self.__sm_symbol_selection_method == 'NUMBER':
            first = self.__find_nonterminal(grammar)
            second = self.__find_nonterminal(grammar)
            return first, second
        else:
            return self.__get_random_nonterminals_pair(grammar)
