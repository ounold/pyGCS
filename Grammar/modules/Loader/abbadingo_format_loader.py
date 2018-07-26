import logging
from typing import List

from modules.Loader.test_data import TestData


class AbbadingoFormatLoader:

    def __init__(self):
        self.__logger = logging.getLogger("abbadingo_format_loader")
        self.__logger.info("Abbadingo Format Loader inited.")
        self.__input_data = []
        self.__filename = ""

    @property
    def input_data(self) -> List[TestData]:
        return self.__input_data

    @property
    def filename(self) -> str:
        return self.__filename

    def load(self, filename):
        self.__filename = filename
        try: 
            with open(self.filename, "r") as f:
                for index_file, line in enumerate(f):
                    test_example = TestData()
                    test_example.id_data = index_file
                    values = line.split(" ")
                    if len(values) > 2:
                        test_example.positive = True if values[0] == "1" else False
                        sequence = ""
                        for index in range(2, len(values)):
                            sequence += values[index]
                        self.__logger.info("Sentence: {0}.".format(sequence))
                        test_example.sequence = sequence.replace("\n", "").lower()
                        self.input_data.append(test_example)
                    else:
                        pass
        except:
            self.__logger.exception("Cannot open file")
            raise
