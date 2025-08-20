# -*- coding: utf-8 -*-
"""
The GetEnumItemHandler class handles retrieving enumeration items.
"""

from importlib import import_module

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class GetEnumItemHandler(AbstractCommandHandler):
    """
    Handler for retrieving enumeration items.
    """

    def __init__(self):
        """
        Initializes a new enumeration item retrieval handler.
        """
        self._required_parameters_count = 3

    def process(self, command):
        """
        Handles the enumeration item retrieval command.

        :param command: Command to handle
        :return: Command execution result
        """
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("CreateEnumHandler parameters mismatch!")
            clazz = command.payload[0]
            enum_name = command.payload[1]
            enum_value = command.payload[2]
            try:
                enum_type = getattr(clazz, enum_name)
                # In Python 2.7, we need to check if the enum_type is a dictionary-like object
                if hasattr(enum_type, '__getitem__'):
                    return enum_type[enum_value]
                else:
                    raise Exception("Enum type does not support item access")
            except AttributeError:
                fields = [field for field in dir(clazz) if not callable(getattr(clazz, field))]
                message = "Enum {} not found in class {}. Available enums:\n".format(enum_name, clazz.__name__)
                for field in fields:
                    message += "{}\n".format(field)
                raise AttributeError(message)
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in GetEnumItemHandler: {0}\n{1}".format(str(e), tb_str)) 