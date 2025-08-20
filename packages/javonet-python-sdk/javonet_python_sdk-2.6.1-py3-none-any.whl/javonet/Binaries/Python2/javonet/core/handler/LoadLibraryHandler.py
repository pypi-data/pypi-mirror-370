# -*- coding: utf-8 -*-
"""
The LoadLibraryHandler class handles library loading.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
import sys
import os
import traceback


class LoadLibraryHandler(AbstractCommandHandler):
    """
    Handler for loading libraries.
    """

    # Class variable to store loaded directories
    loaded_directories = []

    def __init__(self):
        """
        Initializes a new library loading handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        """
        Process the LoadLibrary command.
        
        :param command: Command to process
        :return: 0 on success
        :raises: Exception if parameters mismatch or directory is invalid
        """
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("LoadLibrary payload parameters mismatch")

            # Check if path is a directory and add to sys.path
            if os.path.isdir(command.payload[0]):
                sys.path.append(command.payload[0])
                LoadLibraryHandler.loaded_directories.append(command.payload[0])
            else:
                raise Exception(command.payload[0] + " is not a valid directory")

            return 0
            
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error loading library: {0}\n{1}".format(str(e), tb_str))

    @staticmethod
    def get_loaded_directories():
        """
        Get list of loaded directories.
        
        :return: List of loaded directory paths
        """
        return LoadLibraryHandler.loaded_directories
