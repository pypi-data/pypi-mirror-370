# -*- coding: utf-8 -*-
"""
The PassDelegateHandler class handles delegate passing.
"""

from javonet.core.delegateCache.DelegatesCache import DelegatesCache
from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
import sys
import traceback


class PassDelegateHandler(AbstractCommandHandler):
    """
    Handler for passing delegates.
    """

    def __init__(self):
        """
        Initializes a new delegate passing handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("ResolveInstanceHandler parameters mismatch!")

            # TO BE IMPLEMENTED
            return None
        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in PassDelegateHandler: {0}\n{1}".format(str(e), tb_str)) 