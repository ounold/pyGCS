from enum import Enum


class NegativeExamplesEstimationType(Enum):
    ONLY_POSITIVE_ESTIMATION = 0,
    DIFFERENTIAL_ESTIMATION = 1,
    NO_REGARD_TO_NEGATIVES = 2
