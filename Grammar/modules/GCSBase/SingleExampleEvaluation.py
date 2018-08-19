from modules.GCSBase.domain import CellRule


class SingleExampleEvaluation:
    def __init__(self, m_param=None, m_parsed=None, rules_table=None, fill_rules_table=None, sentence=None, positive = None):
        self.mParam = m_param
        self.mParsed: bool = m_parsed
        self.rulesTable: list[CellRule] = rules_table
        self.full_rules_table = fill_rules_table
        self.sentence = sentence
        self.grammar = None
        self.positive = positive

