# -*- coding: utf-8 -*-
"""
The DelegatesCache module implements caching for delegates.
"""

import uuid
import threading
from javonet.utils.CommandType import CommandType


class DelegatesCache(object):
    """
    Class implementing caching for delegates.
    """
    _instance = None
    delegates_cache = dict()
    _lock = threading.Lock()

    def __new__(cls):
        """
        Creates a new singleton instance of DelegatesCache.

        :return: DelegatesCache instance
        :rtype: DelegatesCache
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DelegatesCache, cls).__new__(cls)
        return cls._instance

    def cache_delegate(self, object_delegate):
        """
        Caches a delegate object.

        :param object_delegate: Delegate to cache
        :return: UUID of the cached delegate
        :rtype: str
        """
        with self._lock:
            uuid_ = str(uuid.uuid4())
            self.delegates_cache[uuid_] = object_delegate
            return uuid_

    def resolve_delegate(self, command):
        """
        Resolves a delegate from the cache.

        :param command: Command containing delegate reference
        :return: Cached delegate
        :raises: Exception if delegate not found
        """
        if command.command_type != CommandType.Reference:
            raise Exception("Failed to find delegate")
        with self._lock:
            try:
                return self.delegates_cache[command.payload[0]]
            except KeyError:
                raise Exception("Object not found in delegates")

    def delete_delegate(self, delegate_guid):
        """
        Deletes a delegate from the cache.

        :param delegate_guid: UUID of the delegate to delete
        :return: 0 if successful
        :raises: Exception if delegate not found
        """
        with self._lock:
            try:
                del self.delegates_cache[delegate_guid]
                return 0
            except KeyError:
                raise Exception("Object not found in delegates") 