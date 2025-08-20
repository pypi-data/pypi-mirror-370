# -*- coding: utf-8 -*-
"""
The GetEnumNameHandler class handles retrieving enumeration names.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
import sys
import traceback


class GetEnumNameHandler(AbstractCommandHandler):
    """
    Handler for retrieving enumeration names.
    """

    def __init__(self):
        """
        Initializes a new enumeration name retrieval handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        """
        Handles the enumeration name retrieval command.

        :param command: Command to handle
        :return: Command execution result
        """
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("CreateEnumHandler parameters mismatch!")
            enum_object = command.payload[0]
            # In Python 2.7 we check if the object has a 'name' attribute
            if hasattr(enum_object, 'name'):
                return enum_object.name
            else:
                raise Exception("Argument is not enumerable or does not have a 'name' attribute")
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in GetEnumNameHandler: {0}\n{1}".format(str(e), tb_str)) 