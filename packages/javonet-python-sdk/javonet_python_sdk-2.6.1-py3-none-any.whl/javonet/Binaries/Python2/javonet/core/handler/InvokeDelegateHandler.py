# -*- coding: utf-8 -*-
"""
The InvokeDelegateHandler class handles delegate invocations.
"""

from javonet.core.delegateCache.DelegatesCache import DelegatesCache
from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
import sys
import traceback


class InvokeDelegateHandler(AbstractCommandHandler):
    """
    Handler for invoking delegates.
    """

    def __init__(self):
        """
        Initializes a new delegate invocation handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("ResolveInstanceHandler parameters mismatch!")

            delegates_cache = DelegatesCache()
            method = delegates_cache.resolve_delegate(command)
            if len(command.payload) > 1:
                method_arguments = command.payload[1:]
                return method(*method_arguments)
            else:
                return method()
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in InvokeDelegateHandler: {0}\n{1}".format(str(e), tb_str))

    def handle(self, command):
        """
        Handles the delegate invocation command.

        :param command: Command to handle
        :return: Command with operation result
        """
        delegate_id = command.get_payload()[0]
        args = command.get_payload()[1:]
        result = Command(command.runtime_name, CommandType.Value, [])
        result = result.add_arg_to_payload(delegate_id)
        for arg in args:
            result = result.add_arg_to_payload(arg)
        return result 