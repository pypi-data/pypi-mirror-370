from javonet.core.delegateCache.DelegatesCache import DelegatesCache
from javonet.core.handler.AbstractCommandHandler import *
from javonet.utils.CommandType import CommandType


class InvokeDelegateHandler(AbstractCommandHandler):

    def __init__(self):
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) < self._required_parameters_count:
                raise Exception(f"{self.__class__.__name__} parameters mismatch")

            delegates_cache = DelegatesCache()
            method = delegates_cache.get_delegate(command.payload[0])
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

            return method(*arguments, **kwargs)
        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None


