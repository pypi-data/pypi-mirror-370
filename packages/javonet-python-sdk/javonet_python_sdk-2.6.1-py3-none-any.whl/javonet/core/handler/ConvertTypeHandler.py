from javonet.core.handler.AbstractCommandHandler import AbstractCommandHandler
from javonet.utils.Type import Type


class ConvertTypeHandler(AbstractCommandHandler):
    def process(self, command):
        return Type.JavonetNoneType
