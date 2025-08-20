# -*- coding: utf-8 -*-
"""
The AbstractCommandHandler class is the base class for command handlers.
"""

from javonet.core.handler.AbstractHandler import AbstractHandler
from javonet.core.handler.HandlerDictionary import handler_dict
from javonet.utils.Command import Command


class AbstractCommandHandler(AbstractHandler):
    """
    Base class for command handlers.
    """
    def process(self, command):
        """
        Process the command. This method should be overridden by subclasses.
        
        :param command: Command to process
        :return: Result of processing
        """
        pass

    def handle_command(self, command):
        """
        Handle the command by iterating through payload and processing it.
        
        :param command: Command to handle
        :return: Result of processing
        """
        self.__iterate(command)
        return self.process(command)

    @staticmethod
    def __iterate(command):
        """
        Iterate through command payload and process nested commands.
        
        :param command: Command with payload to iterate
        """
        for i in range(0, len(command.payload)):
            if isinstance(command.payload[i], Command):
                handler = handler_dict.get(command.payload[i].command_type)
                if handler is not None:
                    command.payload[i] = handler.handle_command(command.payload[i]) 