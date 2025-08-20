# -*- coding: utf-8 -*-
"""
The SetStaticFieldHandler class handles setting static fields.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class SetStaticFieldHandler(AbstractCommandHandler):
    """
    Handler for setting static fields.
    """

    def __init__(self):
        """
        Initializes a new static field setting handler.
        """
        self._required_parameters_count = 3

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("SetStaticFieldHandler parameters mismatch!")

            clazz = command.payload[0]
            field = command.payload[1]
            new_value = command.payload[2]
            try:
                setattr(clazz, field, new_value)
            except AttributeError:
                fields = [field for field in dir(clazz) if not callable(getattr(clazz, field))]
                message = "Field {} not found in class {}. Available fields:\n".format(field, clazz.__name__)
                for field in fields:
                    message += "{}\n".format(field)
                raise AttributeError(message)
            return 0
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in SetStaticFieldHandler: {0}\n{1}".format(str(e), tb_str)) 