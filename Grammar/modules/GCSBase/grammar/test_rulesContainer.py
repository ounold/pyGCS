from unittest import TestCase

from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.grammar.RulesContainer import RulesContainer


class TestRulesContainer(TestCase):
    def test_select_rules_not_used_in_parsing(self):
        rules_container = RulesContainer()
        rule1 = Rule()
        rule1.usages_in_invalid_parsing = 1
        rule2 = Rule()
        rule2.usages_in_invalid_parsing = 0
        rule3 = Rule()
        rule3.usages_in_invalid_parsing = 0
        rule4 = Rule()
        rule4.usages_in_invalid_parsing = 0
        rule5 = Rule()
        rule5.usages_in_invalid_parsing = 2
        rule6 = Rule()
        rule6.usages_in_invalid_parsing = 3

        non_terminal_rules = [rule1, rule2, rule3, rule4, rule5, rule6]
        rules_container.non_terminal_rules = non_terminal_rules

        invalid_usages_rules = rules_container.select_rules_used_in_invalid_parsing()
        self.assertEqual(len(invalid_usages_rules), 3)
        self.assertEqual(invalid_usages_rules[0].usages_in_invalid_parsing, rule1.usages_in_invalid_parsing)
        self.assertEqual(invalid_usages_rules[1].usages_in_invalid_parsing, rule5.usages_in_invalid_parsing)
        self.assertEqual(invalid_usages_rules[2].usages_in_invalid_parsing, rule6.usages_in_invalid_parsing)

    def test_select_rules_not_used_in_parsing_no_invalid_rules(self):
        rules_container = RulesContainer()
        rule1 = Rule()
        rule1.usages_in_invalid_parsing = 0
        rule2 = Rule()
        rule2.usages_in_invalid_parsing = 0
        rule3 = Rule()
        rule3.usages_in_invalid_parsing = 0
        rule4 = Rule()
        rule4.usages_in_invalid_parsing = 0
        rule5 = Rule()
        rule5.usages_in_invalid_parsing = 0
        rule6 = Rule()
        rule6.usages_in_invalid_parsing = 0

        non_terminal_rules = [rule1, rule2, rule3, rule4, rule5, rule6]
        rules_container.non_terminal_rules = non_terminal_rules

        invalid_usages_rules = rules_container.select_rules_used_in_invalid_parsing()
        self.assertEqual(len(invalid_usages_rules), 0)

    def test_select_rules_not_used_in_parsing_all_are_invalid(self):
        rules_container = RulesContainer()
        rule1 = Rule()
        rule1.usages_in_invalid_parsing = 1
        rule2 = Rule()
        rule2.usages_in_invalid_parsing = 2
        rule3 = Rule()
        rule3.usages_in_invalid_parsing = 3
        rule4 = Rule()
        rule4.usages_in_invalid_parsing = 4
        rule5 = Rule()
        rule5.usages_in_invalid_parsing = 5
        rule6 = Rule()
        rule6.usages_in_invalid_parsing = 6

        non_terminal_rules = [rule1, rule2, rule3, rule4, rule5, rule6]
        rules_container.non_terminal_rules = non_terminal_rules

        invalid_usages_rules = rules_container.select_rules_used_in_invalid_parsing()
        self.assertEqual(len(invalid_usages_rules), 6)
        self.assertEqual(invalid_usages_rules[0].usages_in_invalid_parsing, rule1.usages_in_invalid_parsing)
        self.assertEqual(invalid_usages_rules[1].usages_in_invalid_parsing, rule2.usages_in_invalid_parsing)
        self.assertEqual(invalid_usages_rules[2].usages_in_invalid_parsing, rule3.usages_in_invalid_parsing)
        self.assertEqual(invalid_usages_rules[3].usages_in_invalid_parsing, rule4.usages_in_invalid_parsing)
        self.assertEqual(invalid_usages_rules[4].usages_in_invalid_parsing, rule5.usages_in_invalid_parsing)
        self.assertEqual(invalid_usages_rules[5].usages_in_invalid_parsing, rule6.usages_in_invalid_parsing)

    def test_sort_rules_used_in_invalid_parsing(self):
        rules_container = RulesContainer()
        rule1 = Rule()
        rule1.usages_in_invalid_parsing = 1
        rule1.fitness = 0.3
        rule2 = Rule()
        rule2.usages_in_invalid_parsing = 2
        rule2.fitness = 0.29
        rule3 = Rule()
        rule3.usages_in_invalid_parsing = 3
        rule3.fitness = 0.28
        rule4 = Rule()
        rule4.usages_in_invalid_parsing = 4
        rule4.fitness = 0.27
        rule5 = Rule()
        rule5.usages_in_invalid_parsing = 5
        rule5.fitness = 0.26
        rule6 = Rule()
        rule6.usages_in_invalid_parsing = 6
        rule6.fitness = 0.25

        invalid_parsing_rules = [rule1, rule2, rule3, rule4, rule5, rule6]
        sorted_rules = rules_container.sort_rules_used_in_invalid_parsing(invalid_parsing_rules)
        self.assertEqual(sorted_rules[0].fitness, rule6.fitness)
        self.assertEqual(sorted_rules[1].fitness, rule5.fitness)
        self.assertEqual(sorted_rules[2].fitness, rule4.fitness)
        self.assertEqual(sorted_rules[3].fitness, rule3.fitness)
        self.assertEqual(sorted_rules[4].fitness, rule2.fitness)
        self.assertEqual(sorted_rules[5].fitness, rule1.fitness)

