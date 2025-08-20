# -*- coding: utf-8 -*-
"""
The GetTypeHandler class handles retrieving types.
"""

import importlib
import inspect
import logging
import os
import sys
from importlib import import_module

from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.core.handler.LoadLibraryHandler import LoadLibraryHandler
from javonet.core.namespaceCache.NamespaceCache import NamespaceCache
from javonet.core.typeCache.TypeCache import TypeCache
import traceback


class GetTypeHandler(AbstractCommandHandler):
    """
    Handler for retrieving types.
    """

    def __init__(self):
        """
        Initializes a new type retrieval handler.
        """
        self._required_parameters_count = 1
        self.namespace_cache = NamespaceCache()
        self.type_cache = TypeCache()

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception(self.__class__.__name__ + " parameters mismatch!")

            type_to_return = self._get_type_from_payload(command)

            if type_to_return is None:
                raise Exception("Type {} not found".format(command.payload[0]))

            if ((
                    self.namespace_cache.is_namespace_cache_empty() and self.type_cache.is_type_cache_empty()) or  # both caches are empty
                    self.namespace_cache.is_type_allowed(type_to_return) or  # namespace is allowed
                    self.type_cache.is_type_allowed(type_to_return)  # type is allowed
            ):
                pass  # continue - type is allowed
            else:
                allowed_namespaces = ", ".join(self.namespace_cache.get_cached_namespaces())
                allowed_types = ", ".join(self.type_cache.get_cached_types())
                raise Exception(
                    "Type {} not allowed. \nAllowed namespaces: {}\nAllowed types: {}".format(
                        type_to_return.__name__, allowed_namespaces, allowed_types))

            return type_to_return

        except Exception as e:
            # Python 2.7 exception handling
            exc_type, exc_value, exc_traceback = sys.exc_info()
            sys_path = "\n".join(sys.path)
            available_types = "\n".join(self.get_all_available_types())
            new_message = str(e) + "\nLoaded directories:\n" + sys_path + "\nAvailable user types:\n" + available_types + "\n\n\n"
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            raise Exception("Error in GetTypeHandler: {0}\n{1}".format(new_message, tb_str))

    def _get_type_from_payload(self, command):
        """
        Gets a type from the command payload.

        :param command: Command with type information
        :return: Retrieved type
        """
        if len(command.payload) == 1:
            type_name = command.payload[0].split(".")
            # Handle Python 2.7 vs Python 3 module name differences
            if type_name[0] == "builtins":
                type_name[0] = "__builtin__"
            
            if len(type_name) == 1:
                return import_module(type_name[0])
            else:
                return self._get_type_from_nested_payload(type_name)
        else:
            # Handle Python 2.7 vs Python 3 module name differences
            payload = list(command.payload)
            if payload[0] == "builtins":
                payload[0] = "__builtin__"
            
            return self._get_type_from_nested_payload(payload)

    def _get_type_from_nested_payload(self, payload):
        module_name = ".".join(payload[:-1])
        class_name = payload[-1]
        loaded_module = import_module(module_name)
        return getattr(loaded_module, class_name)

    def get_all_available_types(self):
        available_types = set()
        for directory in LoadLibraryHandler.loaded_directories:
            for root, _, files in os.walk(directory):
                if "Binaries" in root:
                    continue
                for file in files:
                    if file.lower().endswith(".py") and file != "__init__.py":
                        module_name = os.path.splitext(file)[0]
                        module_path = os.path.relpath(os.path.join(root, module_name), directory).replace(os.sep, ".")
                        try:
                            module = importlib.import_module(module_path)
                            for name, obj in inspect.getmembers(module, inspect.isclass):
                                qualified_name = "{}.{}".format(module_path, name)
                                available_types.add(qualified_name)
                        except Exception:
                            pass
        return list(available_types) 