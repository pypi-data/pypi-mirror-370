# -*- coding: utf-8 -*-
"""
The SetInstanceFieldHandler class handles setting instance fields.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class SetInstanceFieldHandler(AbstractCommandHandler):
    """
    Handler for setting instance fields.
    """

    def __init__(self):
        """
        Initializes a new instance field setting handler.
        """
        self._required_parameters_count = 3

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("SetInstanceFieldHandler parameters mismatch!")
            instance = command.payload[0]
            field = command.payload[1]
            new_value = command.payload[2]
            try:
                setattr(instance, field, new_value)
            except AttributeError:
                fields = [field for field in dir(instance) if not callable(getattr(instance, field))]
                message = "Field {} not found in class {}. Available fields:\n".format(field, instance.__class__.__name__)
                for field in fields:
                    message += "{}\n".format(field)
                raise AttributeError(message)
            return 0
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in SetInstanceFieldHandler: {0}\n{1}".format(str(e), tb_str)) 