class ProbabilityArrayCell:
    def __init__(self, item_1=0.0, item_2=0.0, *args, **kwargs):
        self.item_1 = item_1
        self.item_2 = item_2

    def __str__(self):
        return 'Item 1: {0}, Item 2: {1}'.format(self.item_1, self.item_2)
