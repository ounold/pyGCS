import pykka


class RulesStorageActor(pykka.ThreadingActor):
    def __init__(self, rules):
        super(RulesStorageActor, self).__init__()
        self.rules = rules

    def update_rules(self, rule):
        self.rules.append(rule)

    def get_rules(self):
        return self.rules
