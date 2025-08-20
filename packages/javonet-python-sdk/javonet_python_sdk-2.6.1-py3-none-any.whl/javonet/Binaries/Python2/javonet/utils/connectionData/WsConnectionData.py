# -*- coding: utf-8 -*-
"""
The WsConnectionData class represents WebSocket connection data.
"""

import hashlib

from javonet.utils.ConnectionType import ConnectionType
from javonet.utils.connectionData.IConnectionData import IConnectionData


class WsConnectionData(IConnectionData):
    """
    Class representing WebSocket connection data.
    """

    def __init__(self, hostname):
        """
        Initializes a new WebSocket connection.

        :param hostname: Host name
        """
        self._hostname = hostname

    @property
    def connection_type(self):
        """
        Returns the connection type.

        :return: Connection type (ConnectionType.WebSocket)
        """
        return ConnectionType.WebSocket

    @property
    def hostname(self):
        """
        Returns the host name.

        :return: Host name
        """
        return self._hostname

    @hostname.setter
    def hostname(self, value):
        """
        Sets the host name.

        :param value: New host name
        """
        self._hostname = value

    def serialize_connection_data(self):
        """
        Serializes connection data to a list of values.

        :return: List containing connection configuration values
        """
        return [self.connection_type.value, 0, 0, 0, 0, 0, 0]

    def __eq__(self, other):
        """
        Compares two WsConnectionData objects.

        :param other: Object to compare
        :return: True if objects are equal, False otherwise
        """
        return isinstance(other, WsConnectionData) and self._hostname == other.hostname

    def __hash__(self):
        """
        Calculates hash value for the object.

        :return: Hash value
        """
        return int(hashlib.sha1(str(self.hostname).encode('utf-8')).hexdigest(), 16) 