import random

from modules.GCSBase.domain.symbol import Symbol
from modules.GCSBase.grammar.grammar import Grammar


class RandomUtils:

    @staticmethod
    def get_random_nonterminal_symbol_from(grammar: Grammar) -> Symbol or None:
        try:
            return random.choice(grammar.nonTerminalSymbols)
        except IndexError:
            return None

    @staticmethod
    def get_random_probability() -> float:
        return random.random()

    @staticmethod
    def make_random_decision_with_probability(probability: float) -> bool:
        return random.random() <= probability
