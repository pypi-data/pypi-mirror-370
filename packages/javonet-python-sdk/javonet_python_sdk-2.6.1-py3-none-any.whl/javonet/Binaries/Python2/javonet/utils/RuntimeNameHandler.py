"""
The RuntimeNameHandler class handles Javonet runtime environment names.
"""

from javonet.utils.RuntimeName import RuntimeName


class RuntimeNameHandler(object):
    """
    Class for handling runtime environment names.
    """

    @staticmethod
    def get_name(runtime_name):
        """
        Returns the runtime environment name as a string.

        :param runtime_name: RuntimeName object representing the runtime environment
        :type runtime_name: RuntimeName
        :return: Runtime environment name as a string
        :rtype: str
        :raises Exception: When the provided runtime name is invalid
        """
        if isinstance(runtime_name, RuntimeName):
            if runtime_name == RuntimeName.clr:
                return "clr"
            elif runtime_name == RuntimeName.go:
                return "go"
            elif runtime_name == RuntimeName.jvm:
                return "jvm"
            elif runtime_name == RuntimeName.netcore:
                return "netcore"
            elif runtime_name == RuntimeName.perl:
                return "perl"
            elif runtime_name == RuntimeName.python:
                return "python"
            elif runtime_name == RuntimeName.ruby:
                return "ruby"
            elif runtime_name == RuntimeName.nodejs:
                return "nodejs"
            elif runtime_name == RuntimeName.cpp:
                return "cpp"
            elif runtime_name == RuntimeName.php:
                return "php"
            elif runtime_name == RuntimeName.python27:
                return "python27"
        raise Exception("Invalid runtime name.") 