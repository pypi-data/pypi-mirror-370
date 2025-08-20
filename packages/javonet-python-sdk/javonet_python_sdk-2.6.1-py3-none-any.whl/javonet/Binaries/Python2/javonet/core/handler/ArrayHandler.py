# -*- coding: utf-8 -*-
"""
The ArrayHandler class is the base class for array operation handlers.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
import sys
import traceback


class ArrayHandler(AbstractCommandHandler):
    """
    Base class for array operation handlers.
    """

    def process(self, command):
        try:
            processedArray = command.payload
            return processedArray

        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in ArrayHandler: {0}\n{1}".format(str(e), tb_str)) 