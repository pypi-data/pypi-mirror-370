# -*- coding: utf-8 -*-
"""
The ArrayGetSizeHandler class handles retrieving array size.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class ArrayGetSizeHandler(AbstractCommandHandler):
    """
    Handler for retrieving array size.
    """

    def __init__(self):
        """
        Initializes a new array size retrieval handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        """
        Handles the array size retrieval command.

        :param command: Command to handle
        :return: Command execution result
        """
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("ArrayGetSizeHandler parameters mismatch!")

            array = command.payload[0]
            size = 1
            while(isinstance(array, list)):
                size = size * len(array)
                array = array[0]

            return size

        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in ArrayGetSizeHandler: {0}\n{1}".format(str(e), tb_str)) 