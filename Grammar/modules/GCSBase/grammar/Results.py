class Results:
    def __init__(self):
        self.true_positive = 0
        self.true_negative = 0
        self.false_positive = 0
        self.false_negative = 0

        self.sensitivity = 0.0
        self.specificity = 0.0
        self.f1 = 0.0
        self.precision = 0.0

        self.count = 0
        self.fitness = 0.0