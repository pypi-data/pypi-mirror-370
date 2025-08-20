# -*- coding: utf-8 -*-
"""
The InvokeStaticMethodHandler class handles static method invocations.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class InvokeStaticMethodHandler(AbstractCommandHandler):
    """
    Handler for invoking static methods.
    """

    def __init__(self):
        """
        Initializes a new static method invocation handler.
        """
        self._required_parameters_count = 2

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("InvokeStaticMethod Parameters mismatch!")

            clazz = command.payload[0]
            try:
                method = getattr(clazz, command.payload[1])
            except AttributeError:
                methods = [method for method in dir(clazz) if callable(getattr(clazz, method))]
                message = "Method {} not found in class {}. Available methods:\n".format(command.payload[1], clazz.__name__)
                for method in methods:
                    message += "{}\n".format(method)
                raise AttributeError(message)
            
            if len(command.payload) > 2:
                method_arguments = command.payload[2:]
                return method(*method_arguments)
            return method()
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in InvokeStaticMethodHandler: {0}\n{1}".format(str(e), tb_str)) 