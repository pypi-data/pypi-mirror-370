# -*- coding: utf-8 -*-
"""
The InvokeGlobalFunctionHandler class handles global function invocations.
"""

import importlib
from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
import sys
import traceback


class InvokeGlobalFunctionHandler(AbstractCommandHandler):
    """
    Handler for invoking global functions.
    """

    def __init__(self):
        """
        Initializes a new global function invocation handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("InvokeGlobalFunction Parameters mismatch! "
                                "Expected at least a fully qualified function name (module.function).")

            # The first payload parameter must be the fully qualified function name,
            # e.g. "my_module.my_function".
            full_function_name = command.payload[0]
            if '.' not in full_function_name:
                raise Exception("Invalid function name format. "
                                "Expected a fully qualified name like 'module_name.function_name'.")

            module_name, function_name = full_function_name.rsplit('.', 1)

            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                raise ImportError("Could not import module '{}'.".format(module_name))

            try:
                function = getattr(module, function_name)
            except AttributeError as e:
                available = [attr for attr in dir(module) if callable(getattr(module, attr))]
                message = ("Function '{}' not found in module '{}'. "
                           "Available functions:\n".format(function_name, module_name) + "\n".join(available))
                raise AttributeError(message)

            if not callable(function):
                raise Exception("Attribute '{}' in module '{}' is not callable.".format(function_name, module_name))

            function_args = command.payload[1:]
            return function(*function_args)

        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in InvokeGlobalFunctionHandler: {0}\n{1}".format(str(e), tb_str))

    def handle(self, command):
        """
        Handles the global function invocation command.

        :param command: Command to handle
        :return: Command with operation result
        """
        function_name = command.get_payload()[0]
        args = command.get_payload()[1:]
        result = Command(command.runtime_name, CommandType.Value, [])
        result = result.add_arg_to_payload(function_name)
        for arg in args:
            result = result.add_arg_to_payload(arg)
        return result 