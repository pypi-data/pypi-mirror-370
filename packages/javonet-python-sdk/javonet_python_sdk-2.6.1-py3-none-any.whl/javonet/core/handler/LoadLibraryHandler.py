import importlib.util
import os
import sys

from javonet.core.handler.AbstractCommandHandler import *


class LoadLibraryHandler(AbstractCommandHandler):
    loaded_directories = []

    def __init__(self):
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("LoadLibrary payload parameters mismatch")

            if os.path.isdir(command.payload[0]):
                sys.path.append(command.payload[0])
                LoadLibraryHandler.loaded_directories.append(command.payload[0])
            elif os.path.isfile(command.payload[0]) and command.payload[0].endswith(".py"):
                module_name = os.path.splitext(os.path.basename(command.payload[0]))[0]
                spec = importlib.util.spec_from_file_location(module_name, command.payload[0])
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                sys.modules[module_name] = module
                LoadLibraryHandler.loaded_directories.append(os.path.dirname(command.payload[0]))
            else:
                raise Exception(command.payload[0] + " is not a valid directory or .py file")

            return 0
        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None

    @staticmethod
    def get_loaded_directories():
        return LoadLibraryHandler.loaded_directories
