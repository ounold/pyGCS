from enum import IntEnum


class SymbolType(IntEnum):
    ST_TERMINAL = 1,
    ST_NON_TERMINAL = 2,
    ST_START = 3,
    ST_UNIVERSAL = 4
