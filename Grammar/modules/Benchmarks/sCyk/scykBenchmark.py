import sys

import os

from modules.Benchmarks.sCyk.scykController import ScykController
from settings.settings import Settings


class Main:
    def __init__(self):
        if len(sys.argv) != 2:
            print("Please set parameters to run app.\nParams: <app_settings_file>")
            sys.exit(1)
        self.__config_app = sys.argv[1]
        if os.path.isfile(self.__config_app):
            self.__settings = Settings(self.__config_app)
        else:
            print(os.path.realpath(self.__config_app))
            sys.exit(1)

    def start(self):
        controller = ScykController(self.__settings)
        controller.run_benchmark()
        sys.exit(0)


if __name__ == "__main__":
    main = Main()
    main.start()
    sys.exit(0)
