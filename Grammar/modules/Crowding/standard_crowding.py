import random
from typing import List, Set

from ..Crowding.crowding import Crowding
from ..GCSBase.domain.Rule import Rule
from ..GCSBase.domain.types.AaaRulesHandlingType import AaaRulesHandlingType
from ..GCSBase.grammar.RulesService import RulesService
from ..GCSBase.grammar.grammar import Grammar


class StandardCrowding(Crowding):

    def __init__(self, settings=None):
        super().__init__(settings)
        if settings:
            self.crowding_factor = int(self.settings.get_value('crowding', 'crowding_factor'))
            self.crowding_population = int(self.settings.get_value('crowding', 'crowding_population'))
            non_terminal_productions = self.settings.get_value('general', 'non_terminal_productions_number')
            self.non_terminal_productions_number = float(non_terminal_productions)
            rules_handling_type = self.settings.get_value('general', 'aaa_rules_handling_type')
            self.aaa_rules_handling_type = AaaRulesHandlingType[rules_handling_type]

    def add_rule(self, grammar: Grammar, new_rule: Rule) -> bool:
        if (self.aaa_rules_handling_type is not AaaRulesHandlingType.NO_AAA_RULES
            or not new_rule.is_non_terminal_to_terminal_terminal_rule()) and \
                        new_rule not in grammar.rulesContainer.forbidden_rules:
            rules = self.initialize_rules(new_rule, grammar)

            if self.rule_already_exist(new_rule, rules):
                self.logger.info("Rule {} exists in grammar".format(new_rule))
                return False

            if self.grammar_has_room_for_rule(rules):
                grammar.add_rule(new_rule)
                self.logger.info("Grammar had room. Rule {} was added".format(new_rule))
                return True

            rule_to_remove = self.find_rule_to_remove(new_rule, rules)

            self.remove_from(grammar, rule_to_remove)
            self.add_to(grammar, new_rule)
            return True

    def add_rules(self, grammar: Grammar, new_rules: List[Rule]) -> None:
        rules = set(grammar.get_non_terminal_rules())

        if self.grammar_has_room_for_rules(new_rules, rules):
            grammar.add_rules(rules)
            return

        rules = self.remove_the_best_rules(rules)
        number_of_rules_to_remove = self.count_rules_to_remove(new_rules, rules)

        for i in range(number_of_rules_to_remove):
            the_worst_rules = self.find_the_worst_rules(rules)
            the_most_similar_rule = self.find_the_most_similar_from(new_rules, among=the_worst_rules)
            grammar.remove_rule(the_most_similar_rule)

        grammar.add_rules(new_rules)
        return

    def count_rules_to_remove(self, new_rules, rules) -> int:
        return rules.__len__() + new_rules.__len__() - int(self.non_terminal_productions_number)

    def grammar_has_room_for_rules(self, new_rules: List[Rule], rules: Set[Rule]) -> bool:
        return rules.__len__() + new_rules.__len__() <= self.non_terminal_productions_number

    def rule_already_exist(self, rule: Rule, rules: Set[Rule]) -> bool:
        return rule in rules

    def remove_the_best_rules(self, rules: Set[Rule]) -> List[Rule]:
        elite_rules_number = int(self.settings.get_value('crowding', 'elite_rules_number'))
        sorted_rules = sorted(rules, key=lambda rule: rule.fitness, reverse=True)
        return sorted_rules[elite_rules_number:]

    def grammar_has_room_for_rule(self, rules: Set[Rule]) -> bool:
        return len(rules) < self.non_terminal_productions_number

    def find_the_most_similar_to(self, rule: Rule, among: List[Rule]) -> Rule:
        return max(among, key=lambda awesome_rule: RulesService.similarities_between_rules(awesome_rule, rule))

    def find_the_worst_rules(self, rules: List[Rule]) -> List[Rule]:
        the_worst_rules = []
        filtered_rules = self.filter_rules(rules)
        for i in range(0, self.crowding_factor):
            subset = self.create_random_subset(filtered_rules, size=self.crowding_population)
            the_worst_rule = self.find_the_worst(subset)
            the_worst_rules.append(the_worst_rule)
        return the_worst_rules

    def filter_rules(self, rules: List[Rule])->List[Rule]:
        filtered_rules = list(filter(lambda rule: rule.age > 0, rules))
        if len(filtered_rules) == 0:
            return rules
        else:
            return filtered_rules

    def find_the_worst(self, rules: List[Rule]) -> Rule:
        return min(rules, key=lambda rule: rule.fitness)

    def create_random_subset(self, rules: List[Rule], size: int) -> List[Rule]:
        if len(rules) <= size:
            return rules
        return random.sample(rules, size)

    def initialize_rules(self, new_rule: Rule, grammar: Grammar) -> Set[Rule]:
        non_terminal_rules = set(grammar.get_non_terminal_rules())
        if self.is_non_terminal_type(new_rule, grammar):
            return self.filter_non_terminal_to_terminal_terminal_rule(non_terminal_rules)
        else:
            return non_terminal_rules

    def is_non_terminal_type(self, new_rule: Rule, grammar: Grammar) -> bool:
        return self.aaa_rules_handling_type is AaaRulesHandlingType.NON_TERMINALS \
               and not new_rule.is_non_terminal_to_terminal_terminal_rule() \
               and grammar.count_Aaa_rules() <= self.non_terminal_productions_number

    def filter_non_terminal_to_terminal_terminal_rule(self, rules: List[Rule]) -> Set[Rule]:
        return [rule for rule in rules if not rule.is_non_terminal_to_terminal_terminal_rule()]

    def find_the_most_similar_from(self, new_rules: List[Rule], among: List[Rule]) -> Rule:
        return max(among, key=lambda awesome_rule: self.count_group_similarity(awesome_rule, new_rules))

    def count_group_similarity(self, new_rule: Rule, rules: List[Rule]) -> int:
        similarity = 0
        for rule in rules:
            similarity += RulesService.similarities_between_rules(new_rule, rule)
        return similarity

    def remove_from(self, grammar: Grammar, rule_to_remove: Rule) -> None:
        self.logger.info("Rule {} removed by crowding".format(rule_to_remove))
        grammar.remove_rule(rule_to_remove)
        self.iteration.remove_crowding_rule(rule_to_remove)

    def add_to(self, grammar: Grammar, rule_to_add) -> None:
        self.logger.info("Rule {} added by crowding".format(rule_to_add))
        grammar.add_rule(rule_to_add)

    def check_the_best_rules_size(self, rules: List[Rule] or Set[Rule]):
        if len(rules) < self.crowding_population:
            raise RuntimeError("Wrong value of crowding_population or elite_rules_number")

    def find_rule_to_remove(self, new_rule: Rule, rules: List[Rule] or Set[Rule]) -> Rule:
        rules = self.remove_the_best_rules(rules)
        self.check_the_best_rules_size(rules)
        the_worst_rules = self.find_the_worst_rules(rules)
        return self.find_the_most_similar_to(new_rule, among=the_worst_rules)
