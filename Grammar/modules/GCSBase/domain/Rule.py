from enum import Enum
from typing import List

from ..domain.symbol import Symbol
from ..domain.types.AaaRulesHandlingType import AaaRulesHandlingType


class RuleOrigin(Enum):
    INITIALIZATION = 'INITIALIZATION'
    COVERING = 'COVERING'
    HEURISTIC = 'HEURISTIC'
    UNKNOWN = 'UNKNOWN'

    def __str__(self):
        return self.value[:1]

class Rule:
    def __init__(self, symbols: List[Symbol] = None):
        self.usages_in_invalid_parsing = 0
        self.usages_in_proper_parsing = 0
        self.right2 = None
        self.right1 = None
        self.fitness = 0
        self.profit = 0.0
        self.debt = 0.0
        self.fertility = 0.0
        self.tmp_used = False
        self.age = 0
        self.lifetime = -1.0
        self.max_depth = 3
        self.is_removable = True
        self.fitness_normalized = 0.0
        self.origin: RuleOrigin = RuleOrigin.UNKNOWN

        if symbols is not None:
            self.left = symbols[0]
            self.right1 = symbols[1]
            if len(symbols) == 3:
                self.right2 = symbols[2]

    def is_terminal(self, rules_handling_type: AaaRulesHandlingType):
        if rules_handling_type == AaaRulesHandlingType.NON_TERMINALS:
            return self.right1.is_terminal() and self.right2 is None
        elif rules_handling_type == AaaRulesHandlingType.TERMINALS:
            return self.right1.is_terminal() and (self.right2 is None or self.right2.is_terminal())
        else:
            return self.right1.is_terminal() and self.right2 is None

    def is_start(self):
        return self.left.is_start()

    def is_non_terminal(self):
        return self.right1.is_non_terminal() or (self.right2 is not None and self.right2.is_non_terminal())

    def is_non_terminal_to_terminal_terminal_rule(self):
        return self.right1.is_terminal() and self.right2 is not None and self.right2.is_terminal()

    def is_reachable(self, grammar, depth=0):
        if self.left.is_start():
            return True
        elif depth == self.max_depth:
            return False
        else:
            is_reachable = False
            for rule in grammar.get_rules():
                if self.left == rule.right1 or self.left == rule.right2:
                    if rule.is_reachable(grammar, depth=depth+1):
                        is_reachable = True
                        break
            return is_reachable

    def is_productive(self, grammar, depth=0):
        if self.is_terminal(AaaRulesHandlingType.NON_TERMINALS):
            return True
        elif depth == self.max_depth:
            return False
        else:
            is_productive = False
            for rule in grammar.get_rules():
                if self.right1 == rule.left or self.right2 == rule.left:
                    if rule.is_productive(grammar, depth=depth+1):
                        is_productive = True
                        break
        return is_productive

    def reset_usages_and_points(self):
        self.usages_in_proper_parsing = 0
        self.usages_in_invalid_parsing = 0
        self.debt = 0.0
        self.profit = 0.0

    def getKey(self):
        return self.fitness

    def __eq__(self, other):
        if type(self) is type(other):
            return self.left == other.left and self.right1 == other.right1 and self.right2 == other.right2
        return False

    def __hash__(self) -> int:
        return hash((self.left, self.right1, self.right2))

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "({} -> {}{} F={} {})".format(self.left, (self.right1 or ""), (self.right2 or ""), self.fitness, self.origin)

    def __cmp__(self, other):
        if hasattr(other, 'fitness'):
            return self.fitness.__cmp__(other.fitness)


