from javonet.core.handler.AbstractCommandHandler import *
from javonet.utils.CommandType import CommandType


class InvokeStaticMethodHandler(AbstractCommandHandler):

    def __init__(self):
        self._required_parameters_count = 2

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception("InvokeStaticMethod Parameters mismatch!")

            clazz = command.payload[0]
            try:
                method = getattr(clazz, command.payload[1])
            except AttributeError:
                methods = [method for method in dir(clazz) if callable(getattr(clazz, method))]
                message = "Method {} not found in class {}. Available methods:\n".format(command.payload[1], clazz.__name__)
                for method in methods:
                    message += "{}\n".format(method)
                raise AttributeError(message)
            
            arguments = []
            kwargs = {}
            if len(command.payload) > 2:
                arguments = command.payload[2:]

                last_arg = arguments[-1]
                if isinstance(last_arg, tuple) and last_arg[0] == CommandType.AsKwargs:
                    if not isinstance(last_arg[1], dict):
                        raise ValueError("Kwargs must be a dictionary, got: " + str(type(last_arg[1]).__name__))
                    kwargs = last_arg[1]
                    arguments = arguments[:-1]

            return method(*arguments, **kwargs)

        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None


