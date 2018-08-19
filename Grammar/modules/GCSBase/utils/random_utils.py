import random
from typing import List

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
    def get_random_nonterminal_symbols_from(grammar: Grammar, number_of_symbols: int) -> List[Symbol] or None:
        try:
            return random.sample(grammar.nonTerminalSymbols, number_of_symbols)
        except ValueError:
            return None

    @staticmethod
    def get_random_probability() -> float:
        return random.uniform(0, 0.5)

    @staticmethod
    def make_random_decision_with_probability(probability: float) -> bool:
        return random.random() <= probability
