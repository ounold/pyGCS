from ..grammar.grammar import Grammar
from typing import List
from ..domain.symbol import Symbol


class SymbolFinder:
    @staticmethod
    def find_symbol_by_char(symbols: List[Symbol], character: str) -> Symbol:
        found_symbol = None
        for symbol in symbols:
            if symbol.value == character:
                found_symbol = symbol
                break
        return found_symbol

    @staticmethod
    def symbols_from_parsed_rule(string_rule: str, symbols: List[Symbol]) -> List[Symbol]:
        string_rule = string_rule.strip()
        split = string_rule.split("->")
        left = SymbolFinder.find_symbol_by_char(symbols, split[0])
        right1 = SymbolFinder.find_symbol_by_char(symbols, split[1][0])

        parsed_symbols = [left, right1]

        if len(split[1]) > 1:
            right2 = SymbolFinder.find_symbol_by_char(symbols, split[1][1])
            if right2 is not None:
                parsed_symbols.append(right2)

        return parsed_symbols

    @staticmethod
    def find_random_nonterminal_symbol(grammar: Grammar) -> Symbol:
        raise NotImplementedError