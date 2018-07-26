from enum import Enum


class AaaRulesHandlingType(Enum):
    TERMINALS = 0,
    NON_TERMINALS = 1,
    NO_AAA_RULES = 2,
    TERMINALS_WITH_RBA = 3,
