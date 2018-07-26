from settings.settings import Settings


class FitnessDefaults:
    def __init__(self, settings: Settings):
        self.non_used_rule_fitness = float(settings.get_value('fitness', 'non_used_rule_fitness'))
        self.weight_fertility_fitness = float(settings.get_value('fitness', 'weight_fertility_fitness'))
        self.weight_proper_prased_rule = float(settings.get_value('fitness', 'weight_proper_prased_rule'))
        self.weight_not_proper_prased_rule = float(settings.get_value('fitness', 'weight_not_proper_parsed_rule'))
        self.weight_classic_fitness = float(settings.get_value('fitness', 'weight_classic_fitness'))
