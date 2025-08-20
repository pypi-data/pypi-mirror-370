import sys
import traceback

from javonet.core.interpreter.Interpreter import Interpreter
from javonet.core.protocol.CommandSerializer import CommandSerializer
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeLogger import RuntimeLogger
from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.connectionData.InMemoryConnectionData import InMemoryConnectionData
from javonet.utils.exception.ExceptionSerializer import ExceptionSerializer
from javonet.utils.messageHelper.MessageHelper import MessageHelper


class Receiver:

    def __init__(self):
        self.connection_data = InMemoryConnectionData()

        # Store the original excepthook
        self.original_excepthook = sys.excepthook

        # Set up global exception handler
        def custom_excepthook(exc_type, exc_value, exc_traceback):
            # Format the exception
            exception_string = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            # Send to App Insights
            MessageHelper.send_message_to_app_insights_sync("ReceiverUnhandledException", exception_string)
            print(exception_string)
            # Call the original handler
            self.original_excepthook(exc_type, exc_value, exc_traceback)

        # Register the custom exception handler
        sys.excepthook = custom_excepthook

    def SendCommand(self, message_byte_array, messageByteArrayLen):
        try:
            result = Interpreter().process(message_byte_array)
            return bytearray(CommandSerializer().serialize(result, self.connection_data))
        except Exception as ex:
            exception_command = ExceptionSerializer.serialize_exception(
                ex,
                Command(RuntimeName.python, CommandType.Exception, [])
            )
            return bytearray(CommandSerializer().serialize(exception_command, self.connection_data))

    def HeartBeat(self, message_byte_array, messageByteArrayLen):
        response_byte_array = bytearray(2)
        response_byte_array[0] = message_byte_array[11]
        response_byte_array[1] = message_byte_array[12] - 2
        return response_byte_array

    def GetRuntimeInfo(self):
        return RuntimeLogger().get_runtime_info()
