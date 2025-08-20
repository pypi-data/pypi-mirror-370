# -*- coding: utf-8 -*-
"""
The EnableNamespaceHandler class handles namespace enabling.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.core.namespaceCache.NamespaceCache import NamespaceCache
import sys
import traceback


class EnableNamespaceHandler(AbstractCommandHandler):
    """
    Handler for enabling namespaces.
    """

    def __init__(self):
        """
        Initializes a new namespace enabling handler.
        """
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception(self.__class__.__name__ + " parameters mismatch!")

            namespace_cache = NamespaceCache()

            for payload in command.payload:
                if isinstance(payload, str):
                    namespace_cache.cache_namespace(payload)
                if isinstance(payload, list):
                    for namespace_to_enable in payload:
                        namespace_cache.cache_namespace(namespace_to_enable)

            return 0

        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in EnableNamespaceHandler: {0}\n{1}".format(str(e), tb_str)) 