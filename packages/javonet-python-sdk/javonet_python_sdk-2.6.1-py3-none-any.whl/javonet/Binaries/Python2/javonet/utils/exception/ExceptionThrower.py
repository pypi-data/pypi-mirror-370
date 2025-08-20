# -*- coding: utf-8 -*-
"""
The ExceptionThrower class is used for throwing exceptions in Javonet.
"""

from javonet.utils.exception.JavonetException import JavonetException
from javonet.utils.ExceptionType import ExceptionType


class ExceptionThrower(object):
    """
    Class for throwing exceptions in Javonet.
    """

    @staticmethod
    def throw_exception(command_exception):
        """
        Throws an exception based on the exception command.

        :param command_exception: Exception command
        :return: Javonet exception
        """
        exception_code = command_exception.payload[0]
        command = command_exception.payload[1]
        exception_name = command_exception.payload[2]
        exception_message = command_exception.payload[3]
        stack_trace_classes = command_exception.payload[4]
        stack_trace_methods = command_exception.payload[5]
        stack_trace_lines = command_exception.payload[6]
        stack_trace_files = command_exception.payload[7]

        stack_trace_elements = ExceptionThrower.process_stack_trace(
            stack_trace_classes,
            stack_trace_methods,
            stack_trace_lines,
            stack_trace_files
        )

        traceback_str = ""
        for element in stack_trace_elements:
            traceback_str += "  File \"{0}\", line {1}, in {2}\n".format(
                element[3], element[2], element[1])

        original_exception = ExceptionType.to_exception(exception_code)

        return ExceptionThrower.create_javonet_exception(
            original_exception,
            exception_message,
            traceback_str
        )

    @staticmethod
    def create_javonet_exception(original_exception, exception_message, traceback_str):
        """
        Creates and returns a Javonet exception.

        :param original_exception: Original exception
        :param exception_message: Exception message
        :param traceback_str: Stack trace
        :return: Javonet exception
        """
        return JavonetException(original_exception.__name__, exception_message, traceback_str)

    @staticmethod
    def process_stack_trace(stack_trace_classes, stack_trace_methods, stack_trace_lines, stack_trace_files):
        """
        Processes stack trace into lists of elements.

        :param stack_trace_classes: Classes in stack trace
        :param stack_trace_methods: Methods in stack trace
        :param stack_trace_lines: Line numbers in stack trace
        :param stack_trace_files: Files in stack trace
        :return: List of stack trace element lists
        """
        stack_trace_elements = []
        if stack_trace_classes:
            classes = stack_trace_classes.split("|")
            methods = stack_trace_methods.split("|")
            lines = stack_trace_lines.split("|")
            files = stack_trace_files.split("|")

            for i in range(len(classes) - 1):
                stack_trace_elements.append([classes[i], methods[i], lines[i], files[i]])

        return stack_trace_elements 