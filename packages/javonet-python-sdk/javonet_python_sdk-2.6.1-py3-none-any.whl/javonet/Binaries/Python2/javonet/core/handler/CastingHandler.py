# -*- coding: utf-8 -*-
"""
The CastingHandler class is the base class for type casting operation handlers.
"""

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler


class CastingHandler(AbstractCommandHandler):
    def process(self, command):
        raise Exception("Explicit cast is forbidden in dynamically typed languages - python.")
