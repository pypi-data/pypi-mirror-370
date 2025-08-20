from javonet.core.handler.AbstractCommandHandler import *
from javonet.core.referenceCache.ReferencesCache import ReferencesCache
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeName import RuntimeName


class ResolveInstanceHandler(AbstractCommandHandler):
    def __init__(self):
        self._required_parameters_count = 1

    def process(self, command):
        try:
            if len(command.payload) != self._required_parameters_count:
                raise Exception("ResolveInstanceHandler parameters mismatch!")

            if command.runtime_name == RuntimeName.python:
                return ReferencesCache().resolve_reference(command)
            else:
                return Command(command.runtime_name, CommandType.Reference, command.payload[0])
        except Exception as e:
            exc_type, exc_value = type(e), e
            new_exc = exc_type(exc_value).with_traceback(e.__traceback__)
            raise new_exc from None
