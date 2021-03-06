from modules.GCSBase.domain.FitnessDefaults import FitnessDefaults
from ..domain.Rule import Rule
from typing import List


class RulesService:
    @staticmethod
    def similarities_between_rules(first_rule: Rule, second_rule: Rule) -> int:
        similarities = 0
        if first_rule.left == second_rule.left:
            similarities += 1
        if first_rule.right1 == second_rule.right1:
            similarities += 1
        if first_rule.right2 == second_rule.right2:
            similarities += 1
        return similarities

    @staticmethod
    def get_description_string_for_rule(rule: Rule) -> List[str]:
        return ["fitness (f): {}".format(rule.fitness),
                "proper usages (u_p): {}".format(rule.usages_in_proper_parsing),
                "invalid usages (u_n): {}".format(rule.usages_in_invalid_parsing),
                "profit (p): {}".format(rule.profit),
                "debt (d): {}".format(rule.debt),
                "age: {}".format(rule.age)]

    @staticmethod
    def count_fitness(ff_max: float, ff_min: float, fitness_defaults: FitnessDefaults, rule: Rule):
        if rule.usages_in_invalid_parsing == 0 and rule.usages_in_proper_parsing == 0:
            f_c = fitness_defaults.non_used_rule_fitness
        else:
            f_c = (fitness_defaults.weight_proper_prased_rule * rule.usages_in_proper_parsing) \
                  / (fitness_defaults.weight_proper_prased_rule * rule.usages_in_proper_parsing +
                     fitness_defaults.weight_not_proper_prased_rule * rule.usages_in_invalid_parsing)

        f_f = 0.0
        if (ff_max - ff_min) != 0:
            f_f = (rule.profit - rule.debt - ff_min) / (ff_max - ff_min)

        rule.fertility = f_f

        fitness = (fitness_defaults.weight_classic_fitness * f_c + fitness_defaults.weight_fertility_fitness * f_f) \
                  / (fitness_defaults.weight_classic_fitness + fitness_defaults.weight_fertility_fitness)
        rule.fitness = fitness

    @staticmethod
    def count_fitness2(r, n_positive, n_negative):
        positive_cover = r.usage_in_distinct_proper / n_positive
        negative_cover = r.usage_in_distinct_invalid / n_negative
        pos_acc = 0 if r.usage_in_distinct_proper == 0 else r.usage_in_distinct_proper_parsed / r.usage_in_distinct_proper
        neg_acc = 0 if r.usage_in_distinct_invalid == 0 else r.usage_in_distinct_invalid_parsed / r.usage_in_distinct_invalid
        pos_gain = positive_cover * pos_acc
        neg_gain = negative_cover * neg_acc
        gain = 0 if (pos_gain + neg_gain) == 0 else pos_gain / (pos_gain + neg_gain)
        #r.fitness = r.fitness * (gain + 1)/10
        r.fitness = gain


