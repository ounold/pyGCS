import logging

from IPython.core.display import display
from ipywidgets import widgets

from modules.Loader.abbadingo_format_loader import AbbadingoFormatLoader
from modules.Visualisation.raport_generator import ReportGenerator
from modules.sGCS.sGCS import sGCS


class CommandController:

    def __init__(self, settings=None):
        self.__settings = settings
        self.__logger = logging.getLogger("command_controller")
        self.__logger.info("Command Controller Module inited.")
        self.__gcs = None
        self.__result_list = []
        self.x__result_generator = None

    @property
    def gcs(self):
        return self.__gcs

    def run_simulation(self):
        train_data_list = self.__settings.get_value("general", "train_set_path").split(",")
        test_data_path = self.__settings.get_value("general", "test_set_path").split(",")
        abbading_format_loader_test = AbbadingoFormatLoader()
        abbading_format_loader_test.load(test_data_path[0])
        for train_data in train_data_list:
            abbading_format_loader = AbbadingoFormatLoader()
            abbading_format_loader.load(train_data)
            try:
                option = self.__settings.get_value("general", "gcs_mode")
                if option == "sGCS":
                    loader_widget = widgets.IntProgress(value=0, min=0, step=1, bar_style='info',
                                                         orientation='horizontal',
                                                         layout=widgets.Layout(width='100%', height='100%'),
                                                         style={'description_width': 'initial'})
                    display(loader_widget)
                    #random.seed(23)
                    self.__gcs = sGCS(self.__settings)
                    self.__gcs.train_data = abbading_format_loader.input_data
                    self.__gcs.test_data = abbading_format_loader_test.input_data
                    self.__gcs.reset_grammar()
                    self.run_standard_test()
                    result = self.__gcs.process(True, loader_widget)
                    result.learning_set_name = train_data
                    self.__result_list.append(str(result))
                    #self.__result_generator = ReportGenerator(result, self.__settings)
                    final_rules = self.__gcs.grammar.get_rules()
                    # for rule in final_rules:
                    #     print(str(rule) + " usages = " + str(rule.usages_in_proper_parsing))
                else:
                    self.__logger.error("Algorithm mode unknown")
            except:
                self.__logger.exception("Parameter not found")
        # print("Done")

    def run_standard_test(self):
        pass
