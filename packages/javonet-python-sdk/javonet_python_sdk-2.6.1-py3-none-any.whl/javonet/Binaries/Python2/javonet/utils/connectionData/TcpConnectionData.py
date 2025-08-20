# -*- coding: utf-8 -*-
"""
The TcpConnectionData class represents TCP connection data.
"""

import hashlib
import socket

from javonet.utils.ConnectionType import ConnectionType
from javonet.utils.connectionData.IConnectionData import IConnectionData


class TcpConnectionData(IConnectionData):
    """
    Class representing TCP connection data.
    """

    def __init__(self, hostname, port):
        """
        Initializes a new TCP connection.

        :param hostname: Host name
        :param port: Port number
        """
        self._hostname = hostname
        self._port = port
        self._ip_address = ""
        if self._hostname == "localhost":
            self._ip_address = "127.0.0.1"
        else:
            try:
                self._ip_address = socket.gethostbyname(self._hostname)
            except socket.gaierror:
                self._ip_address = ""

    @property
    def connection_type(self):
        """
        Returns the connection type.

        :return: Connection type (ConnectionType.Tcp)
        """
        return ConnectionType.Tcp

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

    @property
    def ip_address(self):
        """
        Returns the IP address.

        :return: IP address
        """
        return self._ip_address

    @ip_address.setter
    def ip_address(self, value):
        """
        Sets the IP address.

        :param value: New IP address
        """
        self._ip_address = value

    @property
    def port(self):
        """
        Returns the port number.

        :return: Port number
        """
        return self._port

    @port.setter
    def port(self, value):
        """
        Sets the port number.

        :param value: New port number
        """
        self._port = value

    def serialize_connection_data(self):
        """
        Serializes connection data to a list of values.

        :return: List containing connection configuration values
        """
        address_bytes = self.__get_address_bytes()
        port_bytes = self.__get_port_bytes()
        return [self.connection_type.value] + address_bytes + port_bytes

    def __get_address_bytes(self):
        """
        Converts IP address to a list of bytes.

        :return: List of bytes representing the IP address
        """
        return [int(x) for x in self._ip_address.split(".")]

    def __get_port_bytes(self):
        """
        Converts port number to a list of bytes.

        :return: List of bytes representing the port number
        """
        return [self._port & 0xFF, self._port >> 8]

    def __eq__(self, other):
        """
        Compares two TcpConnectionData objects.

        :param other: Object to compare
        :return: True if objects are equal, False otherwise
        """
        if isinstance(other, TcpConnectionData):
            return self._ip_address == other.ip_address and self._port == other.port
        return False

    def __hash__(self):
        """
        Calculates hash value for the object.

        :return: Hash value
        """
        return int(hashlib.sha1("{0}{1}".format(self._ip_address, self._port).encode()).hexdigest(), 16) 