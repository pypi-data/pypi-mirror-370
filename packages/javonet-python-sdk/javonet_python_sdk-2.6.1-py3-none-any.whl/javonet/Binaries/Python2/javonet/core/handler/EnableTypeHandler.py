# -*- coding: utf-8 -*-
"""
The EnableTypeHandler class handles type enabling.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.core.typeCache.TypeCache import TypeCache
import sys
import traceback


class EnableTypeHandler(AbstractCommandHandler):
    """
    Handler for enabling types.
    """

    def __init__(self):
        """
        Initializes a new type enabling handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception(self.__class__.__name__ + " parameters mismatch!")

            type_cache = TypeCache()

            for payload in command.payload:
                if isinstance(payload, str):
                    type_cache.cache_type(payload)
                if isinstance(payload, list):
                    for type_to_enable in payload:
                        type_cache.cache_type(type_to_enable)

            return 0

        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in EnableTypeHandler: {0}\n{1}".format(str(e), tb_str)) 