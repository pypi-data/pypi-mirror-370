"""
The Transmitter class serves as a facade for TransmitterWrapper.
"""

from javonet.core.transmitter.TransmitterWrapper import TransmitterWrapper


class Transmitter(object):
    """
    Class serving as a facade for TransmitterWrapper.
    """

    @staticmethod
    def send_command(message):
        """
        Sends a command to the native library.

        :param message: Message to send
        :return: Response from the native library
        """
        return TransmitterWrapper().send_command(message)

    @staticmethod
    def activate(license_key):
        """
        Activates Javonet with the provided license key.

        :param license_key: License key
        :return: Activation status code
        """
        return TransmitterWrapper.activate(license_key)

    @staticmethod
    def set_config_source(source_path):
        """
        Sets the configuration source.

        :param source_path: Path to the configuration source
        """
        TransmitterWrapper().set_config_source(source_path)

    @staticmethod
    def set_working_directory(path):
        """
        Sets the working directory.

        :param path: Path to the working directory
        """
        TransmitterWrapper().set_working_directory(path)

    @staticmethod
    def set_javonet_working_directory(path):
        """
        Sets the Javonet working directory.

        :param path: Path to the working directory
        :return: Operation status code
        """
        return TransmitterWrapper.set_javonet_working_directory(path) 