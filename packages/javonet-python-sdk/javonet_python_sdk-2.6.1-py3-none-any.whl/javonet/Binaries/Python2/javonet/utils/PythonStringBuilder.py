# -*- coding: utf-8 -*-
"""
The PythonStringBuilder class provides string building functionality similar to StringBuilder in other languages.
"""

from StringIO import StringIO


class PythonStringBuilder(object):
    """
    Class for building strings efficiently in Python 2.
    """

    def __init__(self):
        """
        Initializes a new string builder.
        """
        self._file_str = StringIO()

    def append(self, string):
        """
        Appends a string to the builder.

        :param string: String to append
        :return: Self for method chaining
        :rtype: PythonStringBuilder
        """
        self._file_str.write(unicode(string))
        return self

    def __str__(self):
        """
        Returns the built string.

        :return: The complete string
        :rtype: str
        """
        return self._file_str.getvalue() 