import copy
import logging
import random
from enum import Enum
from typing import Tuple, Dict, List, Set, Callable
import _pickle as pickle

from numpy.matlib import rand

from modules.Crowding.crowding import Crowding
from modules.GCSBase.domain.Rule import Rule, RuleOrigin
from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.grammar.grammar import Grammar
from modules.GCSBase.utils.random_utils import RandomUtils
from modules.Heuristic.Heuristic import Heuristic
from modules.Visualisation.report_rule import ReportRule
from modules.sGCS.domain.sRule import sRule


class GeneticSelectionType(Enum):
    ROULETTE = 'ROULETTE'
    TOURNAMENT = 'TOURNAMENT'
    RANDOM = 'RANDOM'


class GeneticAlgorithm(Heuristic):

    def __init__(self, crowding: Crowding, settings=None):
        super().__init__(crowding, settings)
        if settings:
            first_selection_type = self.settings.get_value('genetic_algorithm', 'first_rule_selection_type')
            self.first_rule_selection_type = GeneticSelectionType[first_selection_type]

            second_selection_type = self.settings.get_value('genetic_algorithm', 'second_rule_selection_type')
            self.second_rule_selection_type = GeneticSelectionType[second_selection_type]

            tournament_subpopulation = self.settings.get_value('genetic_algorithm',
                                                               'tournament_selection_subpopulation_size')
            self.tournament_selection_subpopulation_size = int(tournament_subpopulation)

            self.crossing_probability = float(self.settings.get_value('genetic_algorithm', 'crossing_probability'))
            self.inversion_probability = float(self.settings.get_value('genetic_algorithm', 'inversion_probability'))
            self.mutation_probability = float(self.settings.get_value('genetic_algorithm', 'mutation_probability'))

            self.new_rules_number = int(self.settings.get_value('genetic_algorithm', 'new_rules_number'))
            self.new_rules_number_percent_unit = self.settings.get_value('genetic_algorithm',
                                                                         'new_rules_number_percent_unit') == "True"

            self.selection = _GeneticSelection(self.tournament_selection_subpopulation_size)
        else:
            self.selection = _GeneticSelection()

    def add_new_rules(self, grammar: Grammar) -> None:
        new_rules_number = self.calculate_number_of_rules_to_add(grammar)
        for i in range(int(new_rules_number / 2)):
            self.add_new_pair(grammar)


    def add_new_pair(self, grammar: Grammar) -> None:
        new_pair = self.run(grammar)
        self.set_origin(new_pair)
        self.add_to_grammar(new_pair, grammar)

    def run(self, grammar: Grammar) -> Tuple[Rule, Rule]:
        parents = self.select(grammar)
        children = self.crossover(parents)

        self.add_to_iteration(parents)

        was_first_inverted = self.invert(children[0])
        was_second_inverted = self.invert(children[1])
        first_mutation_report = self.mutate(children[0], grammar)
        second_mutation_report = self.mutate(children[1], grammar)

        self.first_report_rule = self.create_report_rule(children[0], children[2], was_first_inverted,
                                                         first_mutation_report)
        self.second_report_rule = self.create_report_rule(children[1], children[2], was_second_inverted,
                                                          second_mutation_report)

        return children[0], children[1]

    def select(self, grammar: Grammar) -> Tuple[Rule, Rule]:
        first_rule = self.selection.select_rule(grammar, self.first_rule_selection_type)
        second_rule = self.selection.select_rule(grammar, self.second_rule_selection_type)
        return first_rule, second_rule

    def crossover(self, parents: Tuple[Rule, Rule]) -> Tuple[Rule, Rule, 'CrossoverReport']:
        parents_copy = pickle.loads(pickle.dumps(parents, -1))
        report = CrossoverReport()
        if RandomUtils.make_random_decision_with_probability(self.crossing_probability):
            report = self.cross_rules(parents_copy)
            self.adjust_rules_after_crossover(parents_copy)
        return parents_copy[0], parents_copy[1], report

    def invert(self, rule: Rule) -> bool:
        if RandomUtils.make_random_decision_with_probability(self.inversion_probability):
            self.invert_rule(rule)
            self.adjust_rules_after_inverse(rule)
            return True
        return False

    def add_to_grammar(self, rules: Tuple[Rule, Rule], grammar: Grammar):
        is_added = self.crowding.add_rule(grammar, rules[0])
        if is_added:
            self.logger.info("Added rule: {0}".format(str(rules[0])))
            self.iteration.add_ga_first_rule(self.first_report_rule)
        is_added = self.crowding.add_rule(grammar, rules[1])
        if is_added:
            self.logger.info("Added rule: {0}".format(str(rules[1])))
            self.iteration.add_ga_second_rule(self.second_report_rule)
        return

    def cross_rules(self, pair: Tuple[Rule, Rule]) -> 'CrossoverReport':
        report = CrossoverReport()
        if RandomUtils.make_random_decision_with_probability(0.5):
            pair[0].right1, pair[1].right1 = pair[1].right1, pair[0].right1
            report.first_right_crossed = True
        else:
            pair[0].right2, pair[1].right2 = pair[1].right2, pair[0].right2
            report.second_right_crossed = True
        return report

    def invert_rule(self, rule: Rule) -> None:
        if rule.right2:
            rule.right1, rule.right2 = rule.right2, rule.right1

    def mutate(self, rule: Rule, grammar: Grammar) -> 'MutationReport':
        report = MutationReport()
        left = self.mutate_symbol(rule.left, grammar)
        report.was_left_symbol_mutated = (left == rule.left)
        right1 = self.mutate_symbol(rule.right1, grammar)
        report.was_first_right_symbol_mutated = (right1 == rule.right1)
        right2 = self.mutate_symbol(rule.right2, grammar)
        report.was_second_right_symbol_mutated = (right2 == rule.right2)
        rule.left, rule.right1, rule.right2 = left, right1, right2
        return report

    def mutate_symbol(self, symbol: Symbol, grammar: Grammar) -> Symbol:
        if RandomUtils.make_random_decision_with_probability(self.mutation_probability):
            return RandomUtils.get_random_nonterminal_symbol_from(grammar) or symbol
        else:
            return symbol

    def adjust_rules_after_crossover(self, pair: Tuple[sRule, sRule]) -> None:
        try:
            pair[0].probability, pair[1].probability = pair[1].probability, pair[0].probability
            pair[0].count, pair[1].count = pair[1].count, pair[0].count
            pair[0].positive_count, pair[1].positive_count = pair[1].positive_count, pair[0].positive_count
            pair[0].negative_count, pair[1].negative_count = pair[1].negative_count, pair[0].negative_count
        except AttributeError:
            self.logger.error("Input parameter is not a instance of sRule class")

    def adjust_rules_after_inverse(self, rule: sRule) -> None:
        try:
            rule.probability = 1 - rule.probability
            if rule.count == 0:
                rule.count, rule.positive_count, rule.negative_count = 0, 0, 0
            else:
                rule.count = 1 / rule.count
                rule.positive_count = 1 / rule.positive_count
                rule.negative_count = 1 / rule.negative_count
        except AttributeError:
            self.logger.error(
                "GeneticAlgorithm::adjust_rules_after_inverse - Input parameter is not a instance of sRule class")

    def add_to_iteration(self, parents: Tuple[Rule, Rule]) -> None:
        self.iteration.set_parent_one(parents[0])
        self.iteration.set_parent_two(parents[1])

    def create_report_rule(self, rule: Rule, crossover_report: 'CrossoverReport', was_inverted: bool,
                           mutation_report: 'MutationReport') -> ReportRule:
        report = ReportRule(rule)
        report.right1_crossovered = crossover_report.first_right_crossed
        report.right2_crossovered = crossover_report.second_right_crossed
        report.inverted = was_inverted
        report.left_mutated = mutation_report.was_left_symbol_mutated
        report.right1_mutaded = mutation_report.was_first_right_symbol_mutated
        report.right2_mutated = mutation_report.was_second_right_symbol_mutated
        return report

    def set_origin(self, pair: Tuple[Rule, Rule]):
        for rule in pair:
            rule.origin = RuleOrigin.HEURISTIC

    def calculate_number_of_rules_to_add(self, grammar: Grammar):
        grammar_size = len(grammar.get_non_terminal_rules())
        round_to_even = lambda x: round((x - 0.5) / 2) * 2
        if self.new_rules_number_percent_unit:
            if self.new_rules_number >= 100:
                return round_to_even(grammar_size)
            else:
                return round((grammar_size * self.new_rules_number) / 200) * 2
        else:
            if self.new_rules_number >= len(grammar.get_non_terminal_rules()):
                return round_to_even(grammar_size)
            else:
                return round_to_even(self.new_rules_number)


class _GeneticSelection:

    def __init__(self, tournament_subpopulation_size=5):
        self.tournament_subpopulation_size = tournament_subpopulation_size
        self.selection_map = self.prepare_selection_map()

    def prepare_selection_map(self) -> Dict[GeneticSelectionType, Callable]:
        return {
            GeneticSelectionType.RANDOM: self.random_select,
            GeneticSelectionType.TOURNAMENT: self.tournament_select,
            GeneticSelectionType.ROULETTE: self.roulette_select
        }

    def select_rule(self, grammar: Grammar, selection_type: GeneticSelectionType) -> Rule:
        selection_method = self.selection_map[selection_type]
        return selection_method(grammar.get_non_terminal_rules())

    def random_select(self, rules: Set[Rule]) -> Rule or None:
        return random.sample(rules, 1)

    def tournament_select(self, rules: Set[Rule]) -> Rule:
        subpopulation = self._choose_random_subpopulation(rules, self.tournament_subpopulation_size)
        return self._find_the_best_rule(subpopulation)

    def _choose_random_subpopulation(self, rules: Set[Rule], size: int) -> List[Rule]:
        return random.sample(rules, size)

    def _find_the_best_rule(self, rules: List[Rule]) -> Rule:
        return max(rules, key=lambda rule: rule.fitness)

    def roulette_select(self, rules: Set[Rule]) -> Rule:
        rules_list = self._rules_set_to_list(rules)
        roulette_wheel_size: int = self._sum_fitness(rules_list)
        wheel_sections: List[int] = self._count_sections_of_roulette_wheel(rules_list)
        point_on_wheel: int = random.randint(0, roulette_wheel_size)
        return self._find_rule(rules_list, wheel_sections, point_on_wheel)

    def _rules_set_to_list(self, rules: Set[Rule]) -> List[Rule]:
        return list(rules)

    def _sum_fitness(self, rules: List[Rule]) -> int:
        return int(sum(x.fitness for x in rules))

    def _count_sections_of_roulette_wheel(self, rules: List[Rule]) -> List[int]:
        wheel_ranges = [0] * len(rules)
        wheel_ranges[0] = rules[0].fitness
        for i in range(len(rules) - 1):
            wheel_ranges[i + 1] += rules[i + 1].fitness + wheel_ranges[i]
        return wheel_ranges

    def _find_rule(self, rules: List[Rule], wheel_sections: List[int], point_on_wheel: int) -> Rule:
        rule = rules[0]
        for i in range(len(rules)):
            if wheel_sections[i] > point_on_wheel:
                rule = rules[i]
                break
        return rule


class MutationReport:

    def __init__(self, left: bool = False, first_right: bool = False, second_right: bool = False) -> None:
        self.was_left_symbol_mutated = left
        self.was_first_right_symbol_mutated = first_right
        self.was_second_right_symbol_mutated = second_right


class CrossoverReport:

    def __init__(self, first_right_crossed: bool = False, second_right_crossed: bool = False) -> None:
        self.first_right_crossed = first_right_crossed
        self.second_right_crossed = second_right_crossed
