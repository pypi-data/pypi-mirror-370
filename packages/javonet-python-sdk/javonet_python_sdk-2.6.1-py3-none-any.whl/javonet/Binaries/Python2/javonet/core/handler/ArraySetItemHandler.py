# -*- coding: utf-8 -*-
"""
The ArraySetItemHandler class handles setting array elements.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class ArraySetItemHandler(AbstractCommandHandler):
    """
    Handler for setting array elements.
    """

    def __init__(self):
        """
        Initializes a new array element setting handler.
        """
        self._required_parameters_count = 3

    def process(self, command):
        """
        Handles the array element setting command.

        :param command: Command to handle
        :return: Command execution result
        """
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("ArraySetItemHandler parameters mismatch!")

            array = command.payload[0]

            value = command.payload[2]
            if isinstance(command.payload[1], list):
                indexes = command.payload[1]
            else:
                indexes = [command.payload[1]]

            if isinstance(command.payload[0], dict):
                array[indexes[0]] = value

            # one-dimensional array
            if len(indexes) == 1:
                array[indexes[0]] = value
            # multi-dimensional array
            else:
                for i in range((len(indexes)-1)):
                    array = array[indexes[i]]

                array[indexes[-1]] = value

            return 0

        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in ArraySetItemHandler: {0}\n{1}".format(str(e), tb_str)) 