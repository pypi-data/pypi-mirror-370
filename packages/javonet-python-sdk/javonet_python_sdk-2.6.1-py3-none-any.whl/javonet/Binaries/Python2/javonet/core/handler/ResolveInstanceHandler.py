# -*- coding: utf-8 -*-
import sys
import traceback

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.core.referenceCache.ReferencesCache import ReferencesCache
from javonet.utils.RuntimeName import RuntimeName


class ResolveInstanceHandler(AbstractCommandHandler):
    def __init__(self):
        self._required_parameters_count = 1

    def process(self, command):
        """
        Process the ResolveInstance command.
        
        :param command: Command to process
        :type command: Command
        :return: Resolved instance
        :raises: Exception if parameters mismatch or reference resolution fails
        """
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("ResolveInstanceHandler parameters mismatch!")

            if command.runtime_name == RuntimeName.python27: 
                return ReferencesCache().resolve_reference(command)
            else:
                return Command(command.runtime_name, CommandType.Reference, command.payload[0])
            
        except Exception as e:
            # W Python 2.7 nie ma with_traceback i from None
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error resolving instance: {0}\n{1}".format(str(e), tb_str))
