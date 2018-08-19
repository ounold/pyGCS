import pykka


class RulesAndProbabilityStorage(pykka.ThreadingActor):
    def __init__(self, rules_table, probability_array):
        super(RulesAndProbabilityStorage, self).__init__()
        self.rules_table = rules_table
        self.probability_array = probability_array
        self.rules_to_add = []

    def get_probability_array(self):
        return self.probability_array

    def update_probability_array(self, i, j, k, value):
        self.probability_array[i][j][k] = value

    def update_rules_table(self, i, j, rule):
        self.rules_table[i][j].append(rule)

    def get_rules_table(self):
        return self.rules_table

    def get_rule_to_add(self):
        return self.rules_to_add

    def add_rule_to_add(self, key):
        self.rules_to_add.append(key)
