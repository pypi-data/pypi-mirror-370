# -*- coding: utf-8 -*-
"""
The ValueHandler class handles value operations.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler


class ValueHandler(AbstractCommandHandler):
    """
    Handler for value operations.
    """

    def __init__(self):
        """
        Initializes a new value operations handler.
        """
        pass

    def process(self, command):
        """
        Handles a value operation command.

        :param command: Command to handle
        :return: Command value
        """
        return command.payload[0] 