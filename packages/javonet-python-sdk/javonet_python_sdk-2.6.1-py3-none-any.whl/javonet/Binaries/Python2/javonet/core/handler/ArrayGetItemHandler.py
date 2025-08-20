# -*- coding: utf-8 -*-
"""
The ArrayGetItemHandler class handles retrieving array elements.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
import sys
import traceback


class ArrayGetItemHandler(AbstractCommandHandler):
    """
    Handler for retrieving array elements.
    """

    def __init__(self):
        """
        Initializes a new array element retrieval handler.
        """
        self._required_parameters_count = 2


    def process(self, command):
        """
        Process the command.
        
        :param command: Command to process
        :return: Result of the command
        """
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("ArrayGetItemHandler parameters mismatch!")

            array = command.payload[0]
            if isinstance(command.payload[1], list):
                indexes = command.payload[1]
            else:
                indexes = command.payload[1:]

            array_copy = array[:]  # W Pythonie 2 używamy slicingu zamiast copy()
            for i in indexes:
                array_copy = array_copy[i]
            return array_copy

        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in ArrayGetItemHandler: {0}\n{1}".format(str(e), tb_str)) 