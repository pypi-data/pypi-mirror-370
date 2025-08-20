"""
The Javonet module is a singleton module that serves as the entry point for interacting with Javonet.
It provides functions to activate and initialize the Javonet SDK.
It supports both in-memory and TCP connections.
Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/javonet-static-class>`_ for more information.
"""
import sys
import traceback

from javonet.sdk.ConfigRuntimeFactory import ConfigRuntimeFactory
from javonet.sdk.RuntimeFactory import RuntimeFactory
from javonet.utils.UtilsConst import UtilsConst
from javonet.utils.connectionData.InMemoryConnectionData import InMemoryConnectionData
from javonet.utils.connectionData.TcpConnectionData import TcpConnectionData
from javonet.utils.connectionData.WsConnectionData import WsConnectionData
from javonet.utils.messageHelper.MessageHelper import MessageHelper

MessageHelper.send_message_to_app_insights("SdkMessage", "Javonet SDK initialized")

# Store the original excepthook
original_excepthook = sys.excepthook


# Set up global exception handler
def custom_excepthook(exc_type, exc_value, exc_traceback):
    # Format the exception
    exception_string = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    # Send to App Insights
    MessageHelper.send_message_to_app_insights_sync("SdkUnhandledException", exception_string)
    print(exception_string)
    # Call the original handler
    original_excepthook(exc_type, exc_value, exc_traceback)


# Register the custom exception handler
sys.excepthook = custom_excepthook

def in_memory():
    """
    Initializes Javonet using an in-memory channel on the same machine.

    Returns:
        RuntimeFactory: An instance configured for an in-memory connection.
    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/in-memory-channel>`_ for more information.
    """
    return RuntimeFactory(InMemoryConnectionData())


def tcp(tcp_connection_data: TcpConnectionData):
    """
    Initializes Javonet with a TCP connection to a remote machine.

    Args:
        tcp_connection_data (str): The address of the remote machine.

    Returns:
        RuntimeFactory: An instance configured for a TCP connection.
    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/tcp-channel>`_ for more information.
    """
    return RuntimeFactory(tcp_connection_data)


def web_socket(ws_connection_data: WsConnectionData):
    """
    Initializes Javonet with a WebSocket connection to a remote machine.

    Args:
        ws_connection_data (str): The address of the remote machine.

    Returns:
        RuntimeFactory: An instance configured for a WebSocket connection.
    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/websocket-channel>`_ for more information.
    """
    return RuntimeFactory(ws_connection_data)


def with_config(config_source: str):
    """
    Initializes Javonet with a configuration taken from external source.
    Currently supported: Configuration file in JSON format

    Args:
        config_source (str): Path to a configuration file.

    Returns:
        ConfigRuntimeFactory: An instance configured with configuration data.
    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/configure-channel>`_ for more information.
    """
    return ConfigRuntimeFactory(config_source)


def activate(license_key: str) -> None:
    """
    Activates Javonet with the provided license key.

    Args:
        license_key (str): The license key to activate Javonet.

    Returns:
        int: The activation status code.
    Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/getting-started/activating-javonet>`_ for more information.
    """
    UtilsConst.set_license_key(license_key)


def set_config_source(config_source: str) -> None:
    """
    Sets the configuration source for the Javonet SDK.

    Args:
        config_source (str): The configuration source.
    """
    UtilsConst.set_config_source(config_source)


def set_javonet_working_directory(path: str) -> None:
    """
    Sets the working directory for the Javonet SDK.

    Args:
        path (str): The working directory.
    """
    UtilsConst.set_javonet_working_directory(path)
