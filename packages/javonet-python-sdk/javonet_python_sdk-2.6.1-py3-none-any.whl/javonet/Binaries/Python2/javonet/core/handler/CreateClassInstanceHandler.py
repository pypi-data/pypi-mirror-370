# -*- coding: utf-8 -*-
import inspect
import sys
import traceback

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler


class CreateClassInstanceHandler(AbstractCommandHandler):
    def __init__(self):
        self._required_parameters_count = 1

    def process(self, command):
        """
        Process the CreateClassInstance command.
        
        :param command: Command to process
        :type command: Command
        :return: Created class instance
        :raises: Exception if parameters mismatch or class instantiation fails
        """
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("CreateClassInstanceHandler parameters mismatch!")
            
            clazz = command.payload[0]
            
            if len(command.payload) > 1:
                method_arguments = command.payload[1:]
                return clazz(*method_arguments)
            
            return clazz()
            
        except Exception as e:
            # W Python 2.7 nie ma with_traceback i from None
            # Zamiast tego po prostu rzucamy wyjątek
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error creating class instance: {0}\n{1}".format(str(e), tb_str))
