# -*- coding: utf-8 -*-
"""
The DestructReferenceHandler class handles object reference destruction.
"""

from javonet.core.referenceCache.ReferencesCache import ReferencesCache
from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType


class DestructReferenceHandler(AbstractCommandHandler):
    """
    Handler for object reference destruction.
    """

    def __init__(self):
        """
        Initializes a new reference destruction handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        reference_cache = ReferencesCache()
        return reference_cache.delete_reference(command.payload[0]) 