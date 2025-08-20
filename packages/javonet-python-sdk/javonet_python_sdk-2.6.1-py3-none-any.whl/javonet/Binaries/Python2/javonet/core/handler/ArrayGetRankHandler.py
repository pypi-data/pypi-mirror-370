# -*- coding: utf-8 -*-
"""
The ArrayGetRankHandler class handles retrieving array rank.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
import sys
import traceback


class ArrayGetRankHandler(AbstractCommandHandler):
    """
    Handler for retrieving array rank.
    """

    def __init__(self):
        """
        Initializes a new array rank retrieval handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("ArrayGetRankHandler parameters mismatch!")

            array = command.payload[0]
            rank = 0
            while(isinstance(array, list)):
                rank = rank + 1
                array = array[0]

            return rank

        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in ArrayGetRankHandler: {0}\n{1}".format(str(e), tb_str))
