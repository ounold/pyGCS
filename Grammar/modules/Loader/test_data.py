import logging


class TestData:

    def __init__(self, sequence=None, positive=None, id_data=None):
        self._id_data = id_data
        self.__logger = logging.getLogger("test_example")
        self.__logger.debug("TextExample created.")
        self.__sequence = sequence
        self.__positive = positive

    @property
    def sequence(self):
        return self.__sequence

    @property
    def positive(self):
        return self.__positive

    @property
    def id_data(self):
        return self._id_data

    @sequence.setter
    def sequence(self, sequence):
        self.__logger.info(sequence)
        self.__sequence = sequence

    @positive.setter
    def positive(self, positive):
        self.__logger.info(positive)
        self.__positive = positive

    @id_data.setter
    def id_data(self, id_data):
        self._id_data = id_data
