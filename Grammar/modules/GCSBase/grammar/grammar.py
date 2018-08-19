import logging
import random
import json

from string import ascii_uppercase
from typing import List

import jsonpickle as jsonpickle
from modules.GCSBase.domain.Rule import Rule, RuleOrigin
from modules.GCSBase.domain.symbol import SymbolType
from modules.Loader.test_data import TestData
from .RulesContainer import RulesContainer
from ..domain.symbol import Symbol



class Grammar:
    def __init__(self, settings=None):
        self.symbols = set()
        self.nonTerminalSymbols = set()
        self.terminalSymbols = set()
        self.settings = settings
        self.rulesContainer = RulesContainer(settings)
        self.truePositive = 0
        self.trueNegative = 0
        self.falsePositive = 0
        self.falseNegative = 0
        self.__iteration = None
        self.__logger = logging.getLogger("gcs_base")

    def load_from_json(self):
        with open("grammar.json", "r") as f:
            json_data = f.read()
            self.__dict__ = jsonpickle.decode(json_data)

    def save_to_json(self):
        terminal_symbols = []
        non_terminal_symbols = []
        terminal_rules = []
        non_terminal_rules = []
        for terminal in self.terminalSymbols:
            terminal_symbols.append(terminal.json_str())
        for non_terminal in self.nonTerminalSymbols:
            non_terminal_symbols.append(non_terminal.json_str())
        for terminal_rule in self.rulesContainer.terminal_rules:
            terminal_rules.append(terminal_rule.json_str())
        for non_terminal_rule in self.rulesContainer.non_terminal_rules:
            non_terminal_rules.append(non_terminal_rule.json_str())
        result = {"terminalSymbols": terminal_symbols, "nonTerminalSymbols": non_terminal_symbols,
                  "terminalRules": terminal_rules, "nonTerminalRules": non_terminal_rules}
        return json.dumps(result, indent=4)

    # TODO: not used except tests
    def symbol_index(self, symbol: Symbol) -> int:
        symbols = list(self.terminalSymbols)
        symbols.extend(self.nonTerminalSymbols)
        for s in symbols:
            if s.value == symbol.value:
                return symbols.index(s)
        return -1

    # TODO: not used except tests
    def find_symbol_by_given_index(self, index: int) -> Symbol or None:
        symbols = list(self.terminalSymbols)
        symbols.extend(self.nonTerminalSymbols)
        if 0 <= index < symbols.__len__():
            symbol = symbols.pop(index)
        else:
            symbol = None
        return symbol

    def find_non_terminal_symbol_index(self, non_terminal_symbol: Symbol) -> int:
        for i in range(len(self.nonTerminalSymbols)):
            if self.nonTerminalSymbols[i].value == non_terminal_symbol.value:
                return i
        return -1

    # TODO: add dictionary, not used
    def find_symbol_by_value(self, value: str) -> Symbol or None:
        if self.symbols.__len__() == 0:
            self.symbols = self.__init_symbols__()

        for s in self.symbols:
            if s.value == value:
                return s
        return None

    def calculate_grammar_fitness(self, all_examples: int) -> float:
        if all_examples == 0:
            return 0
        return (self.truePositive + self.trueNegative) / all_examples

    def calculate_sensitivity(self) -> float:
        if self.truePositive == 0 and self.falseNegative == 0:
            return 0
        return self.truePositive / (self.falseNegative + self.truePositive)

    def calculate_precision(self) -> float:
        if self.truePositive == 0 and self.falsePositive == 0:
            return 0
        return self.truePositive / (self.truePositive + self.falsePositive)

    def calculate_specificity(self) -> float:
        if self.trueNegative == 0 and self.falsePositive == 0:
            return 0
        return self.trueNegative / (self.trueNegative + self.falsePositive)

    def calculate_f1(self) -> float:
        if self.calculate_sensitivity() == 0 and self.calculate_precision() == 0:
            return 0
        return 2 * (self.calculate_sensitivity() * self.calculate_precision()) / \
               (self.calculate_sensitivity() + self.calculate_precision())

    def is_grammar_perfectly_fit(self, all_examples: int) -> bool:
        return self.truePositive + self.trueNegative == all_examples

    def remove_unused_rules_and_symbols(self):
        rules_to_delete = set()
        for rule in self.get_rules():
            if rule.usages_in_invalid_parsing == 0 and rule.usages_in_proper_parsing == 0:
                rules_to_delete.add(rule)
        for rule in rules_to_delete:
            self.rulesContainer.remove_rule(rule)

    def remove_bad_rules(self):
        rules_to_remove = []
        for rule in self.rulesContainer.rules:
            if rule.usages_in_proper_parsing == 0:
                rules_to_remove.append(rule)
        for rule in rules_to_remove:
            if self.iteration is not None:
                self.iteration.remove_bad_rule(rule)
            self.rulesContainer.remove_rule(rule)

    def correct_grammar_recursive(self):
        """ This is experimental method. Not used in current version"""
        self.__logger.info("[correct] {0} rules in grammar".format(str(len(self.get_rules()))))
        for rule in self.get_rules():
            self.__logger.info("[correct] Correcting {0}".format(str(rule)))
            if not rule.is_productive(self) or not rule.is_reachable(self):
                self.remove_rule(rule)
                # TODO Trzeba dopisać usuwanie symboli

    def correct_grammar(self):
        used_symbols = set()
        used_rules = set()
        deleted_symbols = set()
        deleted_rules = set()

        rules_handling_type = self.settings.get_value("general", "aaa_rules_handling_type")

        # Productivity
        for rule in self.get_terminal_rules():
            if rule.is_terminal(rules_handling_type):
                used_symbols.add(rule.left)
                used_rules.add(rule)

        while True:
            prev_s_count = len(used_symbols)
            prev_r_count = len(used_rules)

            # get rules that produce symbols in used_symbols
            for s in used_symbols:
                for rule in self.get_rules():
                    if rule.right1 == s or rule.right2 == s:
                        used_rules.add(rule)

            for rule in used_rules:
                if not rule.is_terminal(rules_handling_type):
                    used_symbols.add(rule.right1)
                    used_symbols.add(rule.right2)
                    used_symbols.add(rule.left)

            if len(used_symbols) == prev_s_count and len(used_rules) == prev_r_count:
                break

        for rule in self.get_rules():
            if rule not in used_rules:
                deleted_rules.add(rule)

        for s in self.symbols:
            if s not in used_symbols and s.is_non_terminal():
                deleted_symbols.add(s)

        for rule in deleted_rules:
            self.remove_rule(rule)

        for s in deleted_symbols:
            self.symbols.remove(s)

        # Reachability
        used_symbols = set()
        used_rules = set()
        deleted_symbols = set()
        deleted_rules = set()

        for rule in self.get_rules():
            if rule.is_start():
                used_rules.add(rule)
                used_symbols.add(rule.right1)
                if rule.right2 is not None:
                    used_symbols.add(rule.right2)

        while True:
            prev_s_count = len(used_symbols)
            prev_r_count = len(used_rules)
            for symbol in used_symbols:
                for rule in self.get_rules():
                    if rule.left == symbol:
                        used_rules.add(rule)

            for rule in used_rules:
                if not rule.is_terminal(rules_handling_type):
                    used_symbols.add(rule.right1)
                    used_symbols.add(rule.right2)

            if len(used_symbols) == prev_s_count and len(used_rules) == prev_r_count:
                break

        # self.__logger.info("Exting second do while")

        for rule in self.get_rules():
            if rule not in used_rules:
                deleted_rules.add(rule)
        used_symbols.add(self.get_start_symbol())

        for s in self.symbols:
            if s not in used_symbols and s.is_non_terminal():
                deleted_symbols.add(s)

        for rule in deleted_rules:
            self.__logger.info("Removing" + str(rule))
            # print("Removing {}".format(rule.short()))
            self.remove_rule(rule)

        for s in deleted_symbols:
            self.symbols.remove(s)

    def generate_terminal_symbols_from_data_set(self, train_data):
        # terminal_symbols_list = set()
        for example in train_data:
            for symbol in example.sequence:
                self.symbols.add(Symbol(symbol, symbol_type=SymbolType.ST_TERMINAL))
                self.terminalSymbols.add(Symbol(symbol, symbol_type=SymbolType.ST_TERMINAL))
        self.symbols = list(self.symbols)
        self.terminalSymbols = list(self.terminalSymbols)
        self.nonTerminalSymbols = list(self.nonTerminalSymbols)

    def reset_grammar_symbols_and_rules(self):
        for symbol in self.nonTerminalSymbols:
            self.symbols.remove(symbol)
        self.nonTerminalSymbols.clear()
        self.rulesContainer.clear_rules()

    def clear_grammar(self):
        self.nonTerminalSymbols.clear()
        self.symbols.clear()
        self.terminalSymbols.clear()
        self.rulesContainer.clear_rules()

    def init_grammar(self, data: TestData):
        self.reset_grammar()
        if len(self.terminalSymbols) == 0:
            self.generate_terminal_symbols_from_data_set(data)

        # Adding start symbol
        start_symbol = Symbol("$", SymbolType.ST_START, 0)
        self.nonTerminalSymbols.append(start_symbol)
        self.symbols.append(start_symbol)

        # Adding nonterminal symbols
        char_int = 0

        for i in range(1, int(self.settings.get_value("general", "non_terminal_symbols_number")) + 1):
            new_terminal_symbol_char = ascii_uppercase[char_int]
            n_term_symbol = Symbol(new_terminal_symbol_char, SymbolType.ST_NON_TERMINAL, i)
            self.nonTerminalSymbols.append(n_term_symbol)
            self.symbols.append(n_term_symbol)

            char_int += 1

        # Adding forbidden rules
        if self.settings.get_value("general", "forbid_rules") == "True":
            forbidden_rules = self.settings.get_value("general", "forbidden_rules").split(';')
            for r in forbidden_rules:
                self.rulesContainer.forbidden_rules.append(self.get_rule_rand_non_terminal_rule(
                                                         Symbol(r[0], SymbolType.ST_NON_TERMINAL if r[0] != "$" else SymbolType.ST_START),
                                                         Symbol(r[3], SymbolType.ST_NON_TERMINAL if r[3] != "$" else SymbolType.ST_START),
                                                         Symbol(r[4], SymbolType.ST_NON_TERMINAL if r[4] != "$" else SymbolType.ST_START)))
        # Adding self-defined rules
        if self.settings.get_value("general", "initialize_with_defined_rules") == "True":
            rules_to_add = self.settings.get_value("general", "initialization_rules").split(';')
            if rules_to_add[0]:

                for i in rules_to_add:
                    terminal_rule = True if len(i) == 4 else False
                    rule_to_add = i
                    symbols = []
                    rule_symbols = [i[0], i[3]] if terminal_rule else [i[0], i[3], i[4]]
                    for j in range(len(rule_symbols)):
                        if rule_symbols[j] == "$":
                            s_type = SymbolType.ST_START
                        elif j > 0 and terminal_rule:
                            s_type = SymbolType.ST_TERMINAL
                        else:
                            s_type = SymbolType.ST_NON_TERMINAL
                        if j > 0 and terminal_rule:
                            symbol = Symbol(rule_symbols[j], s_type)
                            symbols.append(symbol)
                            if symbol not in self.terminalSymbols:
                                self.terminalSymbols.append(symbol)
                                self.symbols.append(symbol)
                        else:
                            symbol = Symbol(rule_symbols[j], s_type, len(self.nonTerminalSymbols))
                            symbols.append(symbol)
                            if symbol not in self.nonTerminalSymbols:
                                self.nonTerminalSymbols.append(symbol)
                                self.symbols.append(symbol)
                    if terminal_rule:
                        rule_to_add = self.get_rule_rand_non_terminal_rule(self.nonTerminalSymbols[
                                                                               self.nonTerminalSymbols.index(symbols[0])],
                                                                           self.terminalSymbols[
                                                                               self.terminalSymbols.index(symbols[1])],
                                                                           None)
                    else:
                        rule_to_add = self.get_rule_rand_non_terminal_rule(self.nonTerminalSymbols[
                                                                               self.nonTerminalSymbols.index(symbols[0])],
                                                                           self.nonTerminalSymbols[
                                                                               self.nonTerminalSymbols.index(symbols[1])],
                                                                           self.nonTerminalSymbols[
                                                                               self.nonTerminalSymbols.index(symbols[2])])
                    rule_to_add.origin = RuleOrigin.INITIALIZATION
                    rule_to_add.is_removable = True
                    rule_to_add.age = 1
                    if not self.rulesContainer.does_rule_exists(rule_to_add):
                        self.add_rule(rule_to_add)


        # Adding random terminal productions
        if self.settings.get_value("general", "initialize_with_random_rules") == "True":
            nt_rules_number = len(self.get_non_terminal_rules())
            for i in range(int(self.settings.get_value("general", "each_terminal_productions_number"))):
                for s in self.terminalSymbols:
                    rule_to_add = None
                    while rule_to_add is None or self.rulesContainer.does_rule_exists(rule_to_add):
                        rule_to_add = self.get_rule_rand_non_terminal_rule(random.choice(self.nonTerminalSymbols), s, None)
                        rule_to_add.origin = RuleOrigin.INITIALIZATION
                        rule_to_add.age = 1
                    self.add_rule(rule_to_add)


        # Adding random nonterminal productions
        if self.settings.get_value("general", "initialize_with_random_rules") == "True":
            nt_rules_number = len(self.get_non_terminal_rules())
            for i in range(int(self.settings.get_value("general", "non_terminal_productions_number")) - nt_rules_number):
                rule_to_add = None
                while rule_to_add is None or self.rulesContainer.does_rule_exists(rule_to_add):
                    rule_to_add = self.get_rule_rand_non_terminal_rule(random.choice(self.nonTerminalSymbols),
                                                                       random.choice(self.nonTerminalSymbols),
                                                                       random.choice(self.nonTerminalSymbols))
                    rule_to_add.origin = RuleOrigin.INITIALIZATION
                    rule_to_add.age = 1
                self.add_rule(rule_to_add)
        #self.correct_grammar()

    def reset_grammar(self):
        self.trueNegative = 0
        self.truePositive = 0
        self.falsePositive = 0
        self.falseNegative = 0

    def __init_symbols__(self):
        symbols = list(self.terminalSymbols)
        symbols.extend(self.nonTerminalSymbols)
        return symbols

    def set_iteration(self, iter):
        self.rulesContainer.set_iteration(iter)
        self.__iteration = iter

    @property
    def iteration(self):
        return self.rulesContainer.iteration

    def add_rule(self, rule: Rule) -> None:
        # print("[Grammar] Adding rule rule: {}->{}{} origin={}".format(rule.left, rule.right1, rule.right2, rule.origin))
        self.rulesContainer.add_rule(rule)

    def remove_rule(self, rule: Rule) -> None:
        # print("[Grammar] Removing rule: {}->{}{}".format(rule.left, rule.right1, rule.right2))
        self.rulesContainer.remove_rule(rule)

    def get_rules(self):
        #rules = list(self.rulesContainer.rules)
    #    rules.sort(key=lambda x: str(x.left), reverse=True)
        return self.rulesContainer.rules

    def get_non_terminal_rules(self) -> List[Rule]:
        return self.rulesContainer.non_terminal_rules

    def get_terminal_rules(self) -> List[Rule]:
        return self.rulesContainer.terminal_rules

    def count_Aaa_rules(self):
        return sum(rule.is_non_terminal_to_terminal_terminal_rule() for rule in self.rulesContainer.rules)

    def add_rules(self, rules: List[Rule]) -> None:
        for rule in rules:
            self.rulesContainer.add_rule(rule)

    def get_start_symbol(self) -> Symbol or None:
        try:
            return next(x for x in self.nonTerminalSymbols if x.is_start())
        except StopIteration:
            return None

    def adjust_parameters(self):
        pass

    @staticmethod
    def get_rule_rand_non_terminal_rule(left: Symbol, right1: Symbol, right2: Symbol):
        return Rule([left, right1, right2])

    def __str__(self):
        return "True positives: {} True negatives: {} False positives: {} False negatives: {}" \
            .format(str(self.truePositive), str(self.trueNegative), self.falsePositive, self.falseNegative)

    def shrink_to_proper_size(self, non_terminal_productions_number: int) -> None:
        sorted_rules = sorted(self.get_non_terminal_rules(), key=lambda rule: rule.fitness, reverse=True)
        to_remove = sorted_rules[non_terminal_productions_number:]
        for removed in to_remove:
            self.remove_rule(removed)
            self.__iteration.remove_crowding_rule(removed)

    def calc_metrics(self):
        TP = self.truePositive
        TN = self.trueNegative
        FP = self.falsePositive
        FN = self.falseNegative
        metrics = dict()
        metrics['Sensitivity'] = 0 if (TP + FN) == 0 else TP / (TP + FN)
        metrics['Specificity'] = 0 if (TN + FP) == 0 else TN / (TN + FP)
        metrics['F1'] = 0 if (2*TP + FP + FN) == 0 else 2 * TP / (2*TP + FP + FN)
        metrics['MCC'] = 0 if ((TP + FP)*(TP + FN)*(TN + FP)*(TN+FN))**(1/2) == 0 else \
            ((TP * TN) - (FP * FN)) / ((TP + FP)*(TP + FN)*(TN + FP)*(TN+FN))**(1/2)

        return metrics
