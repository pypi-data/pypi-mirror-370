import platform
import os
import sys


class RuntimeLogger(object):
    """
    Class for logging runtime environment information.
    """
    not_logged_yet = True

    @staticmethod
    def get_runtime_info():
        """
        Gets information about the runtime environment.

        :return: Runtime environment information
        :rtype: str
        """
        try:
            return (
                "Python Managed Runtime Info:\n"
                "Python Version: {0}\n"
                "Python executable path: {1}\n"
                "Python Path: {2}\n"
                "Python Implementation: {3}\n"
                "OS Version: {4} {5}\n"
                "Process Architecture: {6}\n"
                "Current Working Directory: {7}\n"
            ).format(
                platform.python_version(),
                sys.executable,
                sys.path,
                platform.python_implementation(),
                platform.system(),
                platform.version(),
                platform.machine(),
                os.getcwd()
            )
        except Exception as e:
            return "Python Managed Runtime Info: Error while fetching runtime info"

    @staticmethod
    def display_runtime_info():
        """
        Displays information about the runtime environment (only once).
        """
        if RuntimeLogger.not_logged_yet:
            print(RuntimeLogger.get_runtime_info())  # In Python 2 print is not a function
            RuntimeLogger.not_logged_yet = False 