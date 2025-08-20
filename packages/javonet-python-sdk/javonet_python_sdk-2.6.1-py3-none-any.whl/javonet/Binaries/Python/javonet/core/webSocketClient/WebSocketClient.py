import struct

from websockets.protocol import State
from websockets.sync.client import connect

clients = {}
class WebSocketClient:

    def __init__(self, uri: str):
        self.uri = uri
        self.ws = connect(uri, max_size=None)

    @staticmethod
    def add_or_get_client(uri: str) -> 'WebSocketClient':
        client = clients.get(uri)
        if client is not None:
            if not client.ws.protocol.state == State.OPEN:
                client.close()
                client = WebSocketClient(uri)
                clients[uri] = client
        else:
            client = WebSocketClient(uri)
            clients[uri] = client
        return client

    def send_byte_array(self, message: bytes) -> None:
        if self.ws is None:
            raise RuntimeError("WebSocket is not opened")
        self.ws.send(message)

    def receive_byte_array(self) -> bytes:
        response = self.ws.recv()
        if isinstance(response, str):
            response = response.encode('utf-8')
        return response

    def close(self) -> None:
        if self.ws is not None:
            self.ws.close()
            self.ws = None

    @staticmethod
    def send_message(uri: str, message: bytes) -> bytes:
        client = WebSocketClient.add_or_get_client(uri)
        client.send_byte_array(message)
        return client.receive_byte_array()