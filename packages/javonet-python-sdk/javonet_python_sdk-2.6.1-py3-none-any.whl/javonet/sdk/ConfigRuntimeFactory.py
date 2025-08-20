from javonet.sdk.internal.abstract.AbstractConfigRuntimeFactory import AbstractConfigRuntimeFactory
from javonet.sdk.tools.JsonResolver import JsonResolver
from javonet.utils.RuntimeName import RuntimeName
from javonet.sdk.RuntimeContext import RuntimeContext
from javonet.utils.RuntimeNameHandler import RuntimeNameHandler
from javonet.utils.UtilsConst import UtilsConst
from javonet.utils.connectionData.InMemoryConnectionData import InMemoryConnectionData
from javonet.utils.connectionData.TcpConnectionData import TcpConnectionData
from javonet.utils.connectionData.WsConnectionData import WsConnectionData
import os


class ConfigRuntimeFactory(AbstractConfigRuntimeFactory):
    """
    The ConfigRuntimeFactory class implements the AbstractConfigRuntimeFactory interface and provides methods for creating runtime contexts.
    Each method corresponds to a specific runtime (CLR, JVM, .NET Core, Perl, Ruby, Node.js, Python) and returns a RuntimeContext instance for that runtime.
    """

    def __init__(self, config_source):
        self.config_source_ = config_source

    def clr(self, config_name: str = "default"):
        """
        Creates RuntimeContext instance to interact with CLR runtime.

        Args:
			config_name (str): The name of the configuration to use.

        Returns:
            RuntimeContext instance for the CLR runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return ConfigRuntimeFactory._get_runtime_context(self, RuntimeName.clr, config_name)

    def jvm(self, config_name: str = "default"):
        """
        Creates RuntimeContext instance to interact with JVM runtime.

        Args:
			config_name (str): The name of the configuration to use.

        Returns:
            RuntimeContext instance for the JVM runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return ConfigRuntimeFactory._get_runtime_context(self, RuntimeName.jvm, config_name)

    def netcore(self, config_name: str = "default"):
        """
        Creates RuntimeContext instance to interact with .NET runtime.

        Args:
			config_name (str): The name of the configuration to use.

        Returns:
            RuntimeContext instance for the .NET runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return ConfigRuntimeFactory._get_runtime_context(self, RuntimeName.netcore, config_name)

    def perl(self, config_name: str = "default"):
        """
        Creates RuntimeContext instance to interact with Perl runtime.

        Args:
			config_name (str): The name of the configuration to use.

        Returns:
            RuntimeContext instance for the Perl runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return ConfigRuntimeFactory._get_runtime_context(self, RuntimeName.perl, config_name)

    def ruby(self, config_name: str = "default"):
        """
        Creates RuntimeContext instance to interact with Ruby runtime.

        Args:
			config_name (str): The name of the configuration to use.

        Returns:
            RuntimeContext instance for the Ruby runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return ConfigRuntimeFactory._get_runtime_context(self, RuntimeName.ruby, config_name)

    def nodejs(self, config_name: str = "default"):
        """
        Creates RuntimeContext instance to interact with Node.js runtime.

        Args:
			config_name (str): The name of the configuration to use.

        Returns:
            RuntimeContext instance for the Node.js runtime

        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return ConfigRuntimeFactory._get_runtime_context(self, RuntimeName.nodejs, config_name)

    def python(self, config_name: str = "default"):
        """
        Creates RuntimeContext instance to interact with Python runtime.

        Args:
			config_name (str): The name of the configuration to use.
        
        Returns:
            a RuntimeContext instance for the Python runtime
        
        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return ConfigRuntimeFactory._get_runtime_context(self, RuntimeName.python, config_name)

    def python27(self, config_name: str = "default"):
        """
        Creates RuntimeContext instance to interact with Python 2.7 runtime.

        Args:
			config_name (str): The name of the configuration to use.
        
        Returns:
            a RuntimeContext instance for the Python 2.7 runtime
        
        Refer to this `article on Javonet Guides <https://www.javonet.com/guides/v2/python/foundations/runtime-context>`_ for more information.
        """
        return ConfigRuntimeFactory._get_runtime_context(self, RuntimeName.python27, config_name)

    def _get_runtime_context(self, runtime: RuntimeName, config_name: str = "default"):
        """
        Creates a RuntimeContext instance to interact with the specified runtime.

        Args:
            runtime (RuntimeName): The runtime name.
            config_name (str): The configuration name.

        Returns:
            RuntimeContext: A RuntimeContext instance for the specified runtime.
        """

        json_resolver = JsonResolver(self.config_source_)

        try:
            UtilsConst.set_license_key(json_resolver.get_license_key())
        except Exception:
            # licenseKey not found - do nothing
            pass

        try:
            UtilsConst.set_javonet_working_directory(json_resolver.get_working_directory())
        except Exception:
            # workingDirectory not found - do nothing
            pass

        conn_type = json_resolver.get_channel_type(RuntimeNameHandler.get_name(runtime), config_name)

        if conn_type == "inMemory":
            conn_data = InMemoryConnectionData()
        elif conn_type == "tcp":
            conn_data = TcpConnectionData(
                json_resolver.get_channel_host(RuntimeNameHandler.get_name(runtime), config_name),
                json_resolver.get_channel_port(RuntimeNameHandler.get_name(runtime), config_name))
        elif conn_type == "webSocket":
            conn_data = WsConnectionData(
                json_resolver.get_channel_host(RuntimeNameHandler.get_name(runtime), config_name))

        else:
            raise Exception("Invalid connection type")

        rtm_ctx = RuntimeContext.get_instance(runtime, conn_data)
        load_modules(runtime, config_name, json_resolver, rtm_ctx)
        return rtm_ctx


def load_modules(runtime, config_name, jfr, rtm_ctx):
    modules = jfr.get_modules(RuntimeNameHandler.get_name(runtime), config_name).split(',')
    modules = [module.strip() for module in modules if module.strip()]

    config_directory_absolute_path = os.path.dirname(jfr.config_source)

    for module in modules:
        if os.path.isabs(module):
            rtm_ctx.load_library(module)
        else:
            rtm_ctx.load_library(os.path.join(config_directory_absolute_path, module))
