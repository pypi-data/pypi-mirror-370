# -*- coding: utf-8 -*-
"""
The IConnectionData interface defines a contract for classes handling connection data.
"""

from abc import ABCMeta, abstractmethod

from javonet.utils.ConnectionType import ConnectionType


class IConnectionData(object):
    """
    Interface for classes handling connection data.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def connection_type(self):
        """
        Returns the connection type.

        :return: Connection type
        :rtype: ConnectionType
        """
        pass

    @abstractmethod
    def hostname(self):
        """
        Returns the host name.

        :return: Host name
        :rtype: str
        """
        pass

    @abstractmethod
    def serialize_connection_data(self):
        """
        Serializes the connection data.

        :return: Serialized connection data
        :rtype: str
        """
        pass 