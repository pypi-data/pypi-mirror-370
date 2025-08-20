# -*- coding: utf-8 -*-
"""
The AbstractHandler class is the base class for all handlers in Javonet.
"""


class AbstractHandler(object):
    def handle_command(self, command):
        raise NotImplementedError('subclasses must override HandleCommand()!')
