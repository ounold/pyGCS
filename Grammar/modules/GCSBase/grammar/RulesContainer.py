import logging
import sys

from modules.GCSBase.domain.FitnessDefaults import FitnessDefaults
from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.domain.types.AaaRulesHandlingType import AaaRulesHandlingType
from modules.GCSBase.grammar.RulesService import RulesService


class RulesContainer:
    def __init__(self, settings):
        if settings is None:
            raise ValueError('Settings must be provided')
        self.__logger = logging.getLogger('sgcs')
        self.rules = set()
        self.non_terminal_rules = set()
        self.terminal_rules = set()
        self.forbidden_rules = list()
        self.settings = settings
        self.__iteration = None
        rules_handling_type = self.settings.get_value('general', 'aaa_rules_handling_type')
        self.aaa_rules_handling_type = AaaRulesHandlingType[rules_handling_type]
        self.fitness_defaults: FitnessDefaults = FitnessDefaults(self.settings)

    def add_rule(self, rule: Rule):
        if self.aaa_rules_handling_type is not AaaRulesHandlingType.NO_AAA_RULES \
                or not rule.is_non_terminal_to_terminal_terminal_rule():
            self.rules.add(rule)
            if rule.is_terminal(self.aaa_rules_handling_type):
                self.terminal_rules.add(rule)
            else:
                self.non_terminal_rules.add(rule)

    def remove_rule(self, rule):
        # self.rules.remove(rule)
        if rule.is_removable:
            if rule.is_terminal(self.aaa_rules_handling_type):
                try:
                    self.terminal_rules.remove(rule)
                    self.__logger.debug('Removed rule {} from terminal rules'.format(rule))
                except ValueError:
                    self.__logger.debug('Rule {} not found in terminal rules collection during removal'.format(rule))
            else:
                try:
                    self.non_terminal_rules.remove(rule)
                    self.__logger.debug('Removed rule {} from non terminal rules'.format(rule))
                except ValueError:
                    self.__logger.debug('Rule {} not found in non terminal rules collection during removal'.format(rule))
            try:
                self.rules.remove(rule)
                self.__logger.debug('Removed rule {} from all rules'.format(rule))
            except ValueError:
                self.__logger.debug('Rule {} not found in non terminal rules collection during removal'.format(rule))
        else:
            pass

    @property
    def iteration(self):
        return self.__iteration

    def set_iteration(self, iteration):
        self.__iteration = iteration

    def does_rule_exists(self, rule):
        return rule in self.rules

    def clear_rules(self):
        self.rules.clear()
        self.terminal_rules.clear()
        self.non_terminal_rules.clear()

    def get_rule_to_remove_by_reversed_roulette(self):
        rules_list = sorted(self.non_terminal_rules, key=Rule.getKey, reverse=True)
        processed_rules = []

        for i in range(int(self.settings.get_value('general', 'reversed_roulette_rule_count'))):
            if len(rules_list) - 1 - i >= 0:
                processed_rules.append(rules_list[len(rules_list) - 1 - i])

        connections = [0 for x in processed_rules]
        for i in range(len(connections)):
            rule = processed_rules[i]
            for nt_rule in self.non_terminal_rules:
                if nt_rule.left == rule.right1 or nt_rule.left == rule.right2:
                    connections[i] += 2
                if nt_rule.right1 == rule.left or (nt_rule.right2 is not None and nt_rule.right2 == rule.right2):
                    connections[i] += 1

        rule_to_remove = 0
        min_connection = connections[0]
        for i in range(1, len(connections)):
            if connections[i] == min_connection:
                if processed_rules[i].fitness < processed_rules[rule_to_remove].fitness:
                    rule_to_remove = i
                    # TODO: I think this line was missing in original code
                    min_connection = connections[i]
            if connections[i] < min_connection:
                rule_to_remove = i
        return processed_rules[rule_to_remove]

    def select_rules_used_in_invalid_parsing(self):
        return [rule for rule in self.non_terminal_rules if rule.usages_in_invalid_parsing > 0]

    def sort_rules_used_in_invalid_parsing(self, rules_used_in_invalid_parsing):
        return sorted(rules_used_in_invalid_parsing, key=Rule.getKey)

    def count_fitness(self):
        ff_max = sys.float_info.min
        ff_min = sys.float_info.max
        for rule in self.rules:
            rule_ff_value = rule.profit - rule.debt
            if rule_ff_value > ff_max:
                ff_max = rule_ff_value
            if rule_ff_value < ff_min:
                ff_min = rule_ff_value
        for rule in self.rules:
            RulesService.count_fitness(ff_max, ff_min, self.fitness_defaults, rule)

    def count_aaa_rules(self):
        counter = 0
        for rule in self.rules:
            if rule.right1.is_terminal() and rule.right2 is not None and rule.right2.is_terminal():
                counter += 1
        return counter

    # TODO: what is iteration object doing here?
    def reset_usages_and_points(self):
        iteration = None
        for rule in self.rules:
            rule.reset_usages_and_points()

    def make_rules_older(self):
        for rule in self.rules:
            rule.age += 1
