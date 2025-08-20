import os
from javonet.core.handler.Handler import Handler
from javonet.core.protocol.CommandDeserializer import CommandDeserializer
from javonet.core.protocol.CommandSerializer import CommandSerializer
from javonet.utils.ConnectionType import ConnectionType
from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.connectionData.IConnectionData import IConnectionData
from javonet.utils.messageHelper.MessageHelper import MessageHelper

handler = Handler()


class Interpreter:
    debug_mode = os.environ.get("JAVONET_DEBUG") == "TRUE"

    def execute(self, command, connection_data: IConnectionData):
        if self.debug_mode:
            print("Sent command: " + str(command))
            MessageHelper.send_message_to_app_insights("SentCommand", str(command))

        message_byte_array = CommandSerializer().serialize(command, connection_data)

        if connection_data.connection_type == ConnectionType.WebSocket:
            from javonet.core.webSocketClient.WebSocketClient import WebSocketClient
            response_byte_array = WebSocketClient.send_message(connection_data.hostname, message_byte_array)
        elif (command.runtime_name == RuntimeName.python) & (
                connection_data.connection_type == ConnectionType.InMemory):
            from javonet.core.receiver.Receiver import Receiver
            response_byte_array = Receiver().SendCommand(message_byte_array, len(message_byte_array))
        else:
            from javonet.core.transmitter.Transmitter import Transmitter
            response_byte_array = Transmitter.send_command(message_byte_array)

        response = CommandDeserializer(response_byte_array).deserialize()

        if self.debug_mode:
            print("Response command: " + str(response))
            MessageHelper.send_message_to_app_insights("ResponseCommand", str(response))

        return response

    def process(self, message_byte_array):
        received_command = CommandDeserializer(message_byte_array).deserialize()

        if self.debug_mode:
            print("Received command: " + str(received_command))
            MessageHelper.send_message_to_app_insights("ReceivedCommand", str(received_command))

        response = handler.handle_command(received_command)

        if self.debug_mode:
            print("Response command: " + str(response))
            MessageHelper.send_message_to_app_insights("ResponseCommand", str(response))

        return response