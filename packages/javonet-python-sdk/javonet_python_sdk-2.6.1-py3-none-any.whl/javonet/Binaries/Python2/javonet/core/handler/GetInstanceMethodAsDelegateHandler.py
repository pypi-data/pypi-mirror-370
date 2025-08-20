# -*- coding: utf-8 -*-
"""
The GetInstanceMethodAsDelegateHandler class handles retrieving instance methods as delegates.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class GetInstanceMethodAsDelegateHandler(AbstractCommandHandler):
    """
    Handler for retrieving instance methods as delegates.
    """

    def __init__(self):
        """
        Initializes a new instance method as delegate retrieval handler.
        """
        self._required_parameters_count = 2

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("InvokeInstanceMethod Parameters mismatch!")

            class_instance = command.payload[0]
            try:
                method = getattr(class_instance, command.payload[1])
            except AttributeError:
                methods = [method for method in dir(class_instance) if callable(getattr(class_instance, method))]
                message = "Method {} not found in class {}. Available methods:\n".format(command.payload[1],
                                                                                         class_instance.__class__.__name__)
                for method in methods:
                    message += "{}\n".format(method)
                raise AttributeError(message)

            return method
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in GetInstanceMethodAsDelegateHandler: {0}\n{1}".format(str(e), tb_str)) 