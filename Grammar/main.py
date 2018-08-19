import glob
import http.server
import logging
import logging.config
import os
import random
import socketserver
import sys
import threading
import time
import json
from shutil import copy2
from modules.Loader.command_controller import CommandController
from settings.settings import Settings
from modules.Visualisation.raport_generator import ReportGenerator


class MySimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


class Server:
    def __init__(self):
        os.chdir(os.path.join(os.path.dirname(__file__), '../Charts'))
        self._server = socketserver.TCPServer(("0.0.0.0", 8000), MySimpleHTTPRequestHandler)

    def run(self):
        threading.Thread(target=self._server.serve_forever).start()


class Main:
    def __init__(self, jupyter=False):
        if len(sys.argv) not in range(3, 6):
            print("Please set parameters to run app.\nParams: <app_settings_file> <logger_settings_file>")
            sys.exit(1)
        if jupyter:
            self.__config_app = 'app.ini'
            self.__config_logger = 'logger.ini'
        else:
            self.__config_app = sys.argv[1]
            self.__config_logger = sys.argv[2]
        if os.path.isfile(self.__config_app) and os.path.isfile(self.__config_logger):
            #logging.config.fileConfig(self.__config_logger)
            self.__logger = logging.getLogger("main")
            self.__settings = Settings(self.__config_app)
            self._path = "{}/../Charts/data/*.json".format(os.path.dirname(os.path.abspath(__file__)))
            self.report_generator = ReportGenerator(self.__settings)
            files = glob.glob(self._path)
            for f in files:
                os.remove(f)
        else:
            print("Please set valid config paths")
            sys.exit(1)
        self.json_data = json.load(open("./NewTestSets/induced_grammars.json"))

    def archive_old_data(self):
        try:
            date = time.strftime("%Y%m%d-%H%M%S")
            directory_name = "{}/../Charts/data/{}".format(os.path.dirname(os.path.abspath(__file__)), date)
            os.makedirs(directory_name)
            files = glob.glob(self._path)
            for f in files:
                copy2(f, directory_name)
            copy2("{}/app.ini".format(os.path.dirname(os.path.abspath(__file__))), directory_name)
        except IOError as e:
            print("Can't copy files to new directory", e)
        except OSError:
            print("Can't create new directory")

    @property
    def settings(self):
        return self.__settings

    def start(self):
        iterations = int(self.settings.get_value("general", "repeated"))
        self.report_generator.iterations = iterations
        for iteration in range(iterations):
            print("Main module stared. Iteration: {}".format(iteration + 1))
            self.report_generator.current_iteration = iteration
            self.__command_controller = CommandController(self.settings)
            sim_results, final_rules = self.__command_controller.run_simulation()
            self.report_generator.collection_of_iterations.append(sim_results)
            self.report_generator.collection_of_final_rules.append(final_rules)
        visualization_enable = self.settings.get_value("general", "visualization_enable")
        if visualization_enable == "True":
            self.report_generator.create_graphs()
            self.archive_old_data()

    def test(self, type, dataset):
        self.set_settings_for_test(type, dataset)
        self.start()

    def set_settings_for_test(self, type, dataset):
        data = self.json_data
        dataset = data[dataset]
        random_rules = "$->BA;C->BA;C->BB;B->C$;$->AA;$->BB;D->AB;A->$C;B->AA;B->$A"
        self.settings.set_value("general", "initialization_rules", dataset[0]+";"+random_rules)
        self.settings.set_value("general", "train_set_path", dataset[1])
        self.settings.set_value("general", "test_set_path", dataset[1])

        if type == "s_test":
            self.settings.set_value("covering", "is_start_covering_allowed", "False")
            self.settings.set_value("covering", "is_full_covering_allowed", "False")
            self.settings.set_value("covering", "is_universal_covering_allowed", "False")
            self.settings.set_value("covering", "is_terminal_covering_allowed", "False")
            self.settings.set_value("genetic_algorithm", "is_ga_allowed", "False")
            self.settings.set_value("general", "initialize_with_random_rules", "False")
            self.settings.set_value("general", "initialize_with_defined_rules", "True")
        elif type == "f_test":
            self.settings.set_value("covering", "is_start_covering_allowed", "True")
            self.settings.set_value("covering", "is_full_covering_allowed", "True")
            self.settings.set_value("covering", "is_universal_covering_allowed", "True")
            self.settings.set_value("covering", "is_terminal_covering_allowed", "True")
            self.settings.set_value("genetic_algorithm", "is_ga_allowed", "True")
            self.settings.set_value("general", "initialize_with_random_rules", "True")
            self.settings.set_value("general", "initialize_with_defined_rules", "False")
        elif type == "h_test":
            self.settings.set_value("covering", "is_start_covering_allowed", "False")
            self.settings.set_value("covering", "is_full_covering_allowed", "False")
            self.settings.set_value("covering", "is_universal_covering_allowed", "False")
            self.settings.set_value("covering", "is_terminal_covering_allowed", "False")
            self.settings.set_value("genetic_algorithm", "is_ga_allowed", "True")
            self.settings.set_value("general", "initialize_with_random_rules", "True")
            self.settings.set_value("general", "initialize_with_defined_rules", "False")
        elif type == "c_test":
            self.settings.set_value("covering", "is_start_covering_allowed", "True")
            self.settings.set_value("covering", "is_full_covering_allowed", "True")
            self.settings.set_value("covering", "is_universal_covering_allowed", "True")
            self.settings.set_value("covering", "is_terminal_covering_allowed", "True")
            self.settings.set_value("genetic_algorithm", "is_ga_allowed", "False")
            self.settings.set_value("general", "initialize_with_random_rules", "True")
            self.settings.set_value("general", "initialize_with_defined_rules", "False")

    def get_results(self):
        return self.__command_controller.get_result_generator()

    @staticmethod
    def run_server():
        server = Server()
        server.run()


if __name__ == "__main__":
    # print(sys.argv[3], " ", sys.argv[4])
    random.seed(23)
    main = Main()
    if len(sys.argv) == 4:
        print("Choose dataset for testing:")
        [print(x) for x in main.json_data.keys()]
    elif len(sys.argv) == 5:
        main.test(sys.argv[3], sys.argv[4])
    else:
        main.start()
    # main.run_server()
    # print('Done!')
    sys.stdout = open('file', 'w')
    sys.exit(0)
