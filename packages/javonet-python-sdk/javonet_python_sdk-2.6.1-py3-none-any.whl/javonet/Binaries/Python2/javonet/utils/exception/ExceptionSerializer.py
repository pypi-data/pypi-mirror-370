# -*- coding: utf-8 -*-
"""
The ExceptionSerializer class is used for serializing exceptions in Javonet.
"""

import os
import sys
import traceback

from javonet.utils.ExceptionType import ExceptionType
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeName import RuntimeName


class ExceptionSerializer(object):
    """
    Class for serializing exceptions in Javonet.
    """

    Exception = 0
    IOException = 1
    FileNotFoundException = 2
    RuntimeException = 3
    ArithmeticException = 4
    IllegalArgumentException = 5
    IndexOutOfBoundsException = 6
    NullPointerException = 7

    @staticmethod
    def serialize_exception(exception, command):
        """
        Serializes an exception to Javonet command format.

        :param exception: Exception to serialize
        :param command: Command that caused the exception
        :return: Command containing the serialized exception
        """
        exception_command = Command(RuntimeName.python27, CommandType.Exception, [])
        stack_classes = []
        stack_methods = []
        stack_lines = []
        stack_files = []

        try:
            _, _, tb = sys.exc_info()
            trace = traceback.extract_tb(tb)
            exception_message = str(exception)

            exception_name = exception.__class__.__name__

            for frame in trace:
                class_name = ExceptionSerializer.safe_get_class_name(frame)
                method_name = ExceptionSerializer.safe_get_method_name(frame)
                file_name = ExceptionSerializer.safe_get_file_name(frame)
                line = ExceptionSerializer.safe_get_line(frame)

                if "javonet" not in class_name and "reflect" not in class_name:
                    stack_classes.append(class_name)
                    stack_methods.append(method_name)
                    stack_lines.append(str(line))
                    stack_files.append(file_name)

            stack_classes_str = "|".join(stack_classes)
            stack_methods_str = "|".join(stack_methods)
            stack_lines_str = "|".join(stack_lines)
            stack_files_str = "|".join(stack_files)

            exception_command = exception_command.add_arg_to_payload(
                ExceptionSerializer.get_exception_code(exception_name))
            exception_command = exception_command.add_arg_to_payload(str(command) if command else "Command is null")
            exception_command = exception_command.add_arg_to_payload(exception_name)
            exception_command = exception_command.add_arg_to_payload(str(exception_message))
            exception_command = exception_command.add_arg_to_payload(stack_classes_str)
            exception_command = exception_command.add_arg_to_payload(stack_methods_str)
            exception_command = exception_command.add_arg_to_payload(stack_lines_str)
            exception_command = exception_command.add_arg_to_payload(stack_files_str)

        except Exception as ex:
            exception_command = Command(command.runtime_name, CommandType.Exception, [])
            exception_command = exception_command.add_arg_to_payload(
                ExceptionSerializer.get_exception_code(ex.__class__.__name__))

            exception_command = exception_command.add_arg_to_payload(str(command) if command else "Command is null")
            exception_command = exception_command.add_arg_to_payload("Python Exception Serialization Error")
            exception_command = exception_command.add_arg_to_payload(str(ex))
            exception_command = exception_command.add_arg_to_payload("ExceptionSerializer")
            exception_command = exception_command.add_arg_to_payload("serialize_exception")
            exception_command = exception_command.add_arg_to_payload("undefined")
            exception_command = exception_command.add_arg_to_payload("ExceptionSerializer.py")

        return exception_command

    @staticmethod
    def safe_get_class_name(frame):
        try:
            return ExceptionSerializer.format_class_name_from_file(frame[0])
        except Exception:
            return "undefined"

    @staticmethod
    def safe_get_method_name(frame):
        try:
            return frame[2] if frame[2] else "undefined"
        except Exception:
            return "undefined"

    @staticmethod
    def safe_get_file_name(frame):
        try:
            return frame[0] if frame[0] else "undefined"
        except Exception:
            return "undefined"

    @staticmethod
    def safe_get_line(frame):
        try:
            return frame[1] if frame[1] >= 0 else 0
        except Exception:
            return 0

    @staticmethod
    def get_exception_code(exception_name):
        """
        Returns the exception code based on its name.

        :param exception_name: Exception name
        :return: Exception code
        """
        return ExceptionType.to_enum(exception_name)

    @staticmethod
    def format_class_name_from_file(filename):
        """
        Formats the class name based on the file name.

        :param filename: File name
        :return: Class name
        """
        return os.path.splitext((os.path.split(filename)[1]))[0]