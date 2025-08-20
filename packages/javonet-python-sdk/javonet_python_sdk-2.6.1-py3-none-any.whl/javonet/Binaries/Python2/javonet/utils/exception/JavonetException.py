# -*- coding: utf-8 -*-
"""
The JavonetException class represents a Javonet-specific exception.
"""


class JavonetException(Exception):
    """
    Class representing a Javonet-specific exception.
    """

    def __init__(self, name, message, traceback_str):
        """
        Initializes a new Javonet exception.

        :param name: Exception name
        :param message: Exception message
        :param traceback_str: Stack trace
        """
        super(JavonetException, self).__init__(message)
        self.name = name
        self.message = message
        self.traceback_str = traceback_str

    def __str__(self):
        """
        Returns the string representation of the exception.

        :return: String representation of the exception
        """
        return "{0}: {1}\n{2}".format(self.name, self.message, self.traceback_str) 