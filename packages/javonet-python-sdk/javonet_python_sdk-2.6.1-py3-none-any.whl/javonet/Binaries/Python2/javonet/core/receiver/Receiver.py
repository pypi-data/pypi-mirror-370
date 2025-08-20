"""
The Receiver module implements the message receiver.
"""

from javonet.core.interpreter.Interpreter import Interpreter
from javonet.core.protocol.CommandSerializer import CommandSerializer
from javonet.utils.RuntimeLogger import RuntimeLogger
from javonet.utils.connectionData.InMemoryConnectionData import InMemoryConnectionData
from javonet.core.protocol.CommandDeserializer import CommandDeserializer
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.exception.ExceptionSerializer import ExceptionSerializer


class Receiver(object):
    """
    Class implementing the message receiver.
    """

    def __init__(self):
        self.connection_data = InMemoryConnectionData()

    def SendCommand(self, message_byte_array_as_string, messageByteArrayLen):
        try:
            message_byte_array = bytearray(message_byte_array_as_string)
            response_command = Interpreter().process(message_byte_array)
            serialized_response = CommandSerializer().serialize(response_command, self.connection_data)
            return bytearray(serialized_response)
        except Exception as ex:
            exception_command = ExceptionSerializer.serialize_exception(
                ex,
                Command(RuntimeName.python27, CommandType.Exception, [])
            )
            serialized_exception = CommandSerializer().serialize(exception_command, self.connection_data)
            return bytearray(serialized_exception)

    def HeartBeat(self, message_byte_array_as_string, messageByteArrayLen):
        message_byte_array = bytearray(message_byte_array_as_string)
        response_byte_array = bytearray(2)
        response_byte_array[0] = message_byte_array[11]
        response_byte_array[1] = message_byte_array[12] - 2
        return response_byte_array

    def GetRuntimeInfo(self):
        return RuntimeLogger().get_runtime_info()