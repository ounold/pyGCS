
class StochasticExample:
    def __init__(self, sentence, positive, rules, rules_table, probability_array, nonTerminalSymbols):
        self.sentence = sentence
        self.positive = positive
        self.rules = rules
        self.nonTerminalSymbols = nonTerminalSymbols
        self.full_rules_table = rules_table
        self.full_probability_array = probability_array

