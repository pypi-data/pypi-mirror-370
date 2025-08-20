# -*- coding: utf-8 -*-
"""
The GetInstanceFieldHandler class handles retrieving instance fields.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class GetInstanceFieldHandler(AbstractCommandHandler):
    """
    Handler for retrieving instance fields.
    """

    def __init__(self):
        """
        Initializes a new instance field retrieval handler.
        """
        self._required_parameters_count = 2

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("GetInstanceFieldHandler parameters mismatch!")
            clazz = command.payload[0]
            field = command.payload[1]
            try:
                return getattr(clazz, field)
            except AttributeError:
                fields = [field for field in dir(clazz) if not callable(getattr(clazz, field))]
                message = "Field {} not found in class {}. Available fields:\n".format(field, clazz.__class__.__name__)
                for field in fields:
                    message += "{}\n".format(field)
                raise AttributeError(message)
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in GetInstanceFieldHandler: {0}\n{1}".format(str(e), tb_str)) 