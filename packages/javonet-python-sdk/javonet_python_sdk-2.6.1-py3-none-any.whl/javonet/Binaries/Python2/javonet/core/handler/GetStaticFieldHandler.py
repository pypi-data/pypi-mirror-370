# -*- coding: utf-8 -*-
"""
The GetStaticFieldHandler class handles retrieving static fields.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class GetStaticFieldHandler(AbstractCommandHandler):
    """
    Handler for retrieving static fields.
    """

    def __init__(self):
        """
        Initializes a new static field retrieval handler.
        """
        self._required_parameters_count = 2

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("GetStaticFieldHandler parameters mismatch!")
            clazz = command.payload[0]
            field = command.payload[1]
            try:
                value = getattr(clazz, field)
            except:
                fields = [field for field in dir(clazz) if not callable(getattr(clazz, field))]
                message = "Field {} not found in class {}. Available fields:\n".format(field, clazz.__name__)
                for field in fields:
                    message += "{}\n".format(field)
                raise AttributeError(message)
            return value
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in GetStaticFieldHandler: {0}\n{1}".format(str(e), tb_str)) 