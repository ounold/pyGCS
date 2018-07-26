from modules.GCSBase.domain.Rule import Rule
from modules.GCSBase.grammar.RulesService import RulesService

class ReportRule:

    def __init__(self, base_rule=None):
        self.__rule = base_rule
        self.__current_age = None
        self.__fitness = None
        self.__covered = None
        self.__crowding = None
        self.__de_lock_removed = None
        self.__bad_rule = None
        self.__left_mutated = None
        self.__right1_mutaded = None
        self.__right2_mutated = None
        self.__right1_crossovered = None
        self.__right2_crossovered = None
        self.__inverted = None
        self.__is_parent_one = None
        self.__is_parent_two = None
        self.__is_child_one = None
        self.__is_child_two = None
        self.__descriptions = []

    @property
    def rule(self):
        return self.__rule

    @property
    def current_age(self):
        return self.__current_age

    @property
    def fitness(self):
        return self.__fitness

    @property
    def covered(self):
        return self.__covered

    @property
    def crowding(self):
        return self.__crowding

    @property
    def de_lock_removed(self):
        return self.__de_lock_removed

    @property
    def bad_rule(self):
        return self.__bad_rule
    
    @property
    def left_mutated(self):
        return self.__left_mutated

    @property
    def right1_mutaded(self):
        return self.__right1_mutaded

    @property
    def right2_mutated(self):
        return self.__right2_mutated

    @property
    def right1_crossovered(self):
        return self.__right1_crossovered

    @property
    def right2_crossovered(self):
        return self.__right2_crossovered

    @property
    def inverted(self):
        return self.__inverted

    @property
    def is_parent_one(self):
        return self.__is_parent_one

    @property
    def is_parent_two(self):
        return self.__is_parent_two

    @property
    def is_child_one(self):
        return self.__is_child_one

    @property
    def is_child_two(self):
        return self.__is_child_two

    @property
    def descriptions(self):
        return self.__descriptions

    @rule.setter
    def rule(self, rule):
        self.__rule = rule

    @current_age.setter
    def current_age(self, current_age):
        self.__current_age = current_age

    @fitness.setter
    def fitness(self, fitness):
        self.__fitness = fitness

    @covered.setter
    def covered(self, covered):
        self.__covered = covered

    @crowding.setter
    def crowding(self, crowding):
        self.__crowding = crowding

    @de_lock_removed.setter
    def de_lock_removed(self, de_lock_removed):
        self.__de_lock_removed = de_lock_removed

    @bad_rule.setter
    def bad_rule(self, bad_rule):
        self.__bad_rule = bad_rule
    
    @left_mutated.setter
    def left_mutated(self, left_mutated):
        self.__left_mutated = left_mutated

    @right1_mutaded.setter
    def right1_mutaded(self, right1_mutaded):
        self.__right1_mutaded = right1_mutaded

    @right2_mutated.setter
    def right2_mutated(self, right2_mutated):
        self.__right2_mutated = right2_mutated

    @right1_crossovered.setter
    def right1_crossovered(self, right1_crossovered):
        self.__right1_crossovered = right1_crossovered

    @right2_crossovered.setter
    def right2_crossovered(self, right2_crossovered):
        self.__right2_crossovered = right2_crossovered

    @inverted.setter
    def inverted(self, inverted):
        self.__inverted = inverted

    @is_parent_one.setter
    def is_parent_one(self, is_parent_one):
        self.__is_parent_one = is_parent_one

    @is_parent_two.setter
    def is_parent_two(self, is_parent_two):
        self.__is_parent_two = is_parent_two

    @is_child_one.setter
    def is_child_one(self, is_child_one):
        self.__is_child_one = is_child_one

    @is_child_two.setter
    def is_child_two(self, is_child_two):
        self.__is_child_two = is_child_two

    @descriptions.setter
    def descriptions(self, descriptions):
        self.__descriptions = descriptions

    def fill_rule(self):
        self.__fitness = self.__rule.fitness
        self.__current_age = self.__rule.age
        self.__descriptions = RulesService.get_description_string_for_rule(self.__rule)

    def __eq__(self, report_rule):
        if isinstance(report_rule, Rule):
            return self.rule == report_rule
        if type(self) is type(report_rule):
            return report_rule.rule == self.rule
        return False

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "{} -> {}{} P={} Age={} Origin={}".format(self.rule.left, (self.rule.right1 or ""),
                                                         (self.rule.right2 or ""), self.rule.probability,
                                                         self.current_age, self.rule.origin)
