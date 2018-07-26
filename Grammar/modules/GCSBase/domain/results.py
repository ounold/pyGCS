class Results:

    def __init__(self):
        self.__true_positive = None
        self.__true_negative = None
        self.__false_positive = None
        self.__false_negative = None
        self.__sensitivity = None
        self.__specisifity = None
        self.__f1 = None
        self.__precision = None
        self.__count = None
        self.__fitness = None

    @property
    def true_positive(self):
        return self.__true_positive

    @property
    def true_negative(self):
        return self.__true_negative

    @property
    def false_positive(self):
        return self.__false_positive

    @property
    def false_negative(self):
        return self.__false_negative

    @property
    def sensitivity(self):
        return self.__sensitivity

    @property
    def specisifity(self):
        return self.__specisifity

    @property
    def f1(self):
        return self.__f1

    @property
    def precision(self):
        return self.__precision

    @property
    def count(self):
        return self.__count

    @property
    def fitness(self):
        return self.__fitness

    @true_positive.setter
    def true_positive(self, true_positive):
        self.__true_positive = true_positive

    @true_negative.setter
    def true_negative(self, true_negative):
        self.__true_negative = true_negative

    @false_positive.setter
    def false_positive(self, false_positive):
        self.__false_positive = false_positive

    @false_negative.setter
    def false_negative(self, false_negative):
        self.__false_negative = false_negative

    @sensitivity.setter
    def sensitivity(self, sensitivity):
        self.__sensitivity = sensitivity

    @specisifity.setter
    def specisifity(self, specisifity):
        self.__specisifity = specisifity

    @f1.setter
    def f1(self, f1):
        self.__f1 = f1

    @precision.setter
    def precision(self, precision):
        self.__precision = precision

    @count.setter
    def count(self, count):
        self.__count = count

    @fitness.setter
    def fitness(self, fitness):
        self.__fitness = fitness