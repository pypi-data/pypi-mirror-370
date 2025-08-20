import importlib
from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.CommandType import CommandType


class InvokeGlobalFunctionHandler(AbstractCommandHandler):
    def __init__(self):
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("InvokeGlobalFunction Parameters mismatch! "
                                "Expected at least a fully qualified function name (module.function).")

            # The first payload parameter must be the fully qualified function name,
            # e.g. "my_module.my_function".
            full_function_name = command.payload[0]
            if '.' not in full_function_name:
                raise Exception("Invalid function name format. "
                                "Expected a fully qualified name like 'module_name.function_name'.")

            module_name, function_name = full_function_name.rsplit('.', 1)

            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                raise ImportError(f"Could not import module '{module_name}'.") from e

            try:
                function = getattr(module, function_name)
            except AttributeError as e:
                available = [attr for attr in dir(module) if callable(getattr(module, attr))]
                message = (f"Function '{function_name}' not found in module '{module_name}'. "
                           "Available functions:\n" + "\n".join(available))
                raise AttributeError(message) from e

            if not callable(function):
                raise Exception(f"Attribute '{function_name}' in module '{module_name}' is not callable.")

            arguments = []
            kwargs = {}
            if len(command.payload) > 1:
                arguments = command.payload[1:]

                last_arg = arguments[-1]
                if isinstance(last_arg, tuple) and last_arg[0] == CommandType.AsKwargs:
                    if not isinstance(last_arg[1], dict):
                        raise ValueError("Kwargs must be a dictionary, got: " + str(type(last_arg[1]).__name__))
                    kwargs = last_arg[1]
                    arguments = arguments[:-1]

            return function(*arguments, **kwargs)

        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None
