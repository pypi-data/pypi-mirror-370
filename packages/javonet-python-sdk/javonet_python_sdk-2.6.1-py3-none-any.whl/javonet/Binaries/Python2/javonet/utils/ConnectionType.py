"""
Connection type with the runtime.
"""

class ConnectionType(object):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, ConnectionType):
            return self.value == other.value
        return False

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self._name_map.get(self.value, str(self.value))

    def __repr__(self):
        return "ConnectionType." + str(self)

    InMemory = None
    Tcp = None
    WebSocket = None

    _name_map = {
        0: 'InMemory',
        1: 'Tcp',
        2: 'WebSocket'
    }

# Initialize values
ConnectionType.InMemory = ConnectionType(0)
ConnectionType.Tcp = ConnectionType(1)
ConnectionType.WebSocket = ConnectionType(2) 