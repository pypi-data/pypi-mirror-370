import struct
import websocket
from websocket import ABNF, WebSocketConnectionClosedException

clients = {}

class WebSocketClient(object):
    def __init__(self, uri):
        self.uri = uri
        # establish a sync connection
        self.ws = websocket.create_connection(uri)

    @staticmethod
    def add_or_get_client(uri):
        client = clients.get(uri)
        if client is not None:
            # if the socket has been closed, reconnect
            if not getattr(client.ws, 'connected', False):
                client.close()
                client = WebSocketClient(uri)
                clients[uri] = client
        else:
            client = WebSocketClient(uri)
            clients[uri] = client
        return client

    def send_byte_array(self, message):
        if self.ws is None:
            raise RuntimeError("WebSocket is not opened")
        try:
            # force binary opcode for raw bytes
            self.ws.send(message, opcode=ABNF.OPCODE_BINARY)
        except WebSocketConnectionClosedException:
            raise RuntimeError("WebSocket is closed, cannot send")

    def receive_byte_array(self):
        if self.ws is None:
            raise RuntimeError("WebSocket is not opened")
        try:
            response = self.ws.recv()
        except WebSocketConnectionClosedException:
            raise RuntimeError("WebSocket is closed, cannot receive")
        # on Py2, recv() might give unicode for text frames
        if isinstance(response, unicode):  
            response = response.encode('utf-8')
        return response

    def close(self):
        if self.ws is not None:
            self.ws.close()
            self.ws = None

    @staticmethod
    def send_message(uri, message):
        client = WebSocketClient.add_or_get_client(uri)
        client.send_byte_array(message)
        return client.receive_byte_array()