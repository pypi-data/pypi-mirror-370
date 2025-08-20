import threading
from typing import Any, Callable, Dict, Optional, Type
import importlib
import os

from javonet.sdk.InvocationContext import InvocationContext
from javonet.sdk.tools.ActivatorDetails import ActivatorDetails
from javonet.sdk.tools.typeParsingFunctions import JavaTypeParsingFunctions, NetcoreTypeParsingFunctions, NodejsTypeParsingFunctions, PythonTypeParsingFunctions

class ComplexTypeResolver:
    _instance = None
    _instance_lock = threading.Lock()          # protects singleton creation

    _type_map: Dict[str, ActivatorDetails] = {}
    _type_map_lock = threading.RLock()         # protects _type_map reads/writes
    
    _type_parsing_functions: Dict[str, Dict[str, Callable[[InvocationContext], Any]]] = {
        "netcore": NetcoreTypeParsingFunctions.ParsingFunctions,
        "jvm": JavaTypeParsingFunctions.ParsingFunctions,
        "nodejs": NodejsTypeParsingFunctions.ParsingFunctions,
        "python": PythonTypeParsingFunctions.ParsingFunctions,
    }

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:           # double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, result_type: str, type_: Type, args: Optional[list] = None):
        with self._type_map_lock:
            if result_type not in self._type_map:
                self._type_map[result_type] = ActivatorDetails(type_, args)

    def convert_result(self, ic: InvocationContext) -> Any:
        runtime_dict = self._type_parsing_functions.get(ic.get_runtime_name().name)
        if runtime_dict:
            parsing_func = runtime_dict.get(ic.get_result_type())
            if parsing_func:
                return parsing_func(ic)

        with self._type_map_lock:
            activator_details = self._type_map.get(ic.get_result_type())
        if not activator_details:
            raise KeyError(f"No type registered for key '{ic.get_result_type()}'.")

        return activator_details.type(*activator_details.arguments)

    @staticmethod
    def resolve_type(type_name: str, module_name: Optional[str] = None) -> Type:
        if module_name:
            if module_name.endswith('.py'):
                module_name = os.path.splitext(os.path.basename(module_name))[0]

            module = importlib.import_module(module_name)
            type_obj = getattr(module, type_name, None)
            if type_obj is None:
                raise ImportError(f"Type '{type_name}' not found in module '{module_name}'")
            return type_obj

        # Assume type is built-in or already imported
        type_obj = globals().get(type_name)
        if type_obj is None:
            raise ImportError(f"Type '{type_name}' not found in global scope")
        return type_obj