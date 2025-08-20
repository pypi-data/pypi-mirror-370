# -*- coding: utf-8 -*-
"""
The HandlerDictionary class stores a dictionary of command handlers.
"""

# Global dictionary for handlers
handler_dict = {}


class HandlerDictionary(object):
    """
    Class for managing command handlers dictionary.
    """

    @staticmethod
    def add_handler_to_dict(command_type, handler):
        """
        Add a handler to the dictionary.
        
        :param command_type: Type of command
        :param handler: Handler for the command
        """
        handler_dict[command_type] = handler 