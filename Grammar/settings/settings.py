from configparser import ConfigParser
import logging


class Settings:

    def __init__(self, configFile):
        self.__logger = logging.getLogger('settings')
        self.__config_parser = ConfigParser()
        self.__config_parser.read(configFile)
        self.__logger.info("Initilized Settings")
        self.weightProperPrasedRule = 1.0
        self.weightNonproperParsedRule = 1.0
        self.weightFertilityFitness = 1.0
        self.nonUsedRuleFitness = 0.5
        self.weightClassicFitness = 1.0

    def get_value(self, section, key):
        try:
            value = self.__config_parser.get(section=section, option=key)
            # self.__logger.debug("Getting section {0} and key {1}. Value of key: {2}".format(section , key, value))
            return value
        except:
            self.__logger.exception("Cannot get key or section from settings")
            return False

    def set_value(self, section, key, value):
        try:
            self.__config_parser.set(section=section, option=key, value=value)
            self.__logger.debug("Setting value {0} for section {1} and key {2}".format(value, section , key))
        except:
            self.__logger.exception("Cannot set value to settings")
