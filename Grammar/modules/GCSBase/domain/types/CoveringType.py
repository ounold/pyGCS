from enum import Enum


class CoveringType(Enum):
    RANDOM = 0,
    NAKAMURA = 1,
    SMART_COVERING = 2,
    SMART_WITH_TABU = 3
