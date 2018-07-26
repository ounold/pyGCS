import logging
from modules.Visualisation.report_rule import ReportRule
from typing import List


class Iteration:

    def __init__(self):
        self.__rules = []
        self.__added = []
        self.__removed = []
        self.__results = None
        self.__result_map = dict()
        self.__grammar_size = None
        self.__terminal_rules = None
        self.__terminal_rules_list = set()
        self.__non_terminal_rules = None
        self.__non_terminal_rules_list = set()
        self.__aaa_rules = None
        self.sentence_rules_parsing_data = list()

    @property
    def rules(self):
        return self.__rules

    @property
    def added(self):
        return self.__added

    @property
    def removed(self):
        return self.__removed

    @property
    def results(self):
        return self.__results

    @property
    def result_map(self):
        return self.__result_map

    @property
    def grammar_size(self):
        return self.__grammar_size

    @property
    def terminal_rules(self):
        return self.__terminal_rules

    @property
    def non_terminal_rules(self):
        return self.__non_terminal_rules

    @property
    def terminal_rules_list(self):
        return self.__terminal_rules_list

    @property
    def non_terminal_rules_list(self):
        return self.__non_terminal_rules_list

    @property
    def aaa_rules(self):
        return self.__aaa_rules

    @rules.setter
    def rules(self, rules):
        self.__rules = rules

    @added.setter
    def added(self, added):
        self.__added = added

    @removed.setter
    def removed(self, removed):
        self.__removed = removed

    @results.setter
    def results(self, results):
        self.__results = results

    @result_map.setter
    def result_map(self, result_map):
        self.__result_map = result_map

    @grammar_size.setter
    def grammar_size(self, grammar_size):
        self.__grammar_size = grammar_size

    @terminal_rules.setter
    def terminal_rules(self, terminal_rules):
        self.__terminal_rules = terminal_rules

    @non_terminal_rules.setter
    def non_terminal_rules(self, non_terminal_rules):
        self.__non_terminal_rules = non_terminal_rules

    @terminal_rules_list.setter
    def terminal_rules_list(self, terminal_rules):
        self.__terminal_rules_list = terminal_rules

    @non_terminal_rules_list.setter
    def non_terminal_rules_list(self, non_terminal_rules):
        self.__non_terminal_rules_list = non_terminal_rules

    @aaa_rules.setter
    def aaa_rules(self, aaa_rules):
        self.__aaa_rules = aaa_rules

    def add_rules(self, standard_rules=[]):
        for rule in standard_rules:
            self.__rules.append(ReportRule(rule))

    def fill_report_rules(self):
        for rule in self.added:
            rule.fill_rule()
        for rule in self.removed:
            rule.fill_rule()
        for rule in self.rules:
            rule.fill_rule()

    def add_covering_rule(self, rule):
        # print("[Iteration] add_covering_rule - {0}".format(rule))
        covering_rule = ReportRule(rule)
        covering_rule.covered = True
        self.added.append(covering_rule)

    def get_ga_rule(self, rule):
        return ReportRule(rule)

    def remove_rule(self, rule):
        try:
            if rule in self.added:
                self.added.remove(rule)
            if rule in self.rules:
                self.rules.remove(rule)
            self.removed.append(rule)
        except:
            print("Rule not found")

    def remove_crowding_rule(self, rule):
        report_rule = self.get_rule(rule)
        report_rule.crowding = True
        self.remove_rule(report_rule)

    def remove_selective_de_lock_rule(self, rule):
        report_rule = self.get_rule(rule)
        report_rule.de_lock_removed = True
        self.remove_rule(report_rule)

    def remove_bad_rule(self, rule):
        report_rule = self.get_rule(rule)
        report_rule.bad_rule = True
        self.remove_rule(report_rule)

    def add_ga_first_rule(self, report_rule):
        report_rule.is_child_one = True
        self.added.append(report_rule)

    def add_ga_second_rule(self, report_rule):
        report_rule.is_child_two = True
        self.added.append(report_rule)

    def set_parent_one(self, rule):
        self.get_rule(rule).is_parent_one = True

    def set_parent_two(self, rule):
        self.get_rule(rule).is_parent_two = True

    def get_rule(self, rule):
        for report_rule in self.added:
            if report_rule == rule:
                return report_rule
        for report_rule in self.rules:
            if report_rule == rule:
                return report_rule
        for report_rule in self.removed:
            if report_rule == rule:
                return report_rule
        print("Rule not found: {}".format(rule))
        print("Added rules: {}".format(self.added))
        print("Removed rules: {}".format(self.removed))
        print("Rules: {}".format(self.rules))
        return None

    def set_final_production_number(self, terminals, non_terminals, aaa, terminals_list, non_terminals_list):
        self.__grammar_size = terminals + non_terminals
        self.__terminal_rules = terminals
        self.__non_terminal_rules = non_terminals
        self.__aaa_rules = aaa
        self.non_terminal_rules_list = non_terminals_list
        self.__terminal_rules_list = terminals_list

    def add_to_result_map(self, key, value):
        self.result_map[key] = value
