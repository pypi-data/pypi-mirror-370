# -*- coding: utf-8 -*-
"""
The GetEnumValueHandler class handles retrieving enumeration element values.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class GetEnumValueHandler(AbstractCommandHandler):
    """
    Handler for retrieving enumeration element values.
    """

    def __init__(self):
        """
        Initializes a new enumeration value retrieval handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("CreateEnumHandler parameters mismatch!")
            enum_object = command.payload[0]
            # In Python 2.7 we check if the object has a 'value' attribute
            if hasattr(enum_object, 'value'):
                return enum_object.value
            else:
                raise Exception("Argument is not enumerable or does not have a 'value' attribute")
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in GetEnumValueHandler: {0}\n{1}".format(str(e), tb_str)) 