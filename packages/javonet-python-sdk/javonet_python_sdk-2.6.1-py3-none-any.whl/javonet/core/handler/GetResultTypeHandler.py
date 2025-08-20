from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils import CommandType


class GetResultTypeHandler(AbstractCommandHandler):
    def __init__(self):
        self._required_parameters_count = 1

    def process(self, command):
        return f"{command.payload[0].__class__.__module__}.{command.payload[0].__class__.__name__}"