# -*- coding: utf-8 -*-
import re
import types
import threading


class TypeCache(object):
    _instance = None
    type_cache = list()
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._lock.acquire()
            try:
                if cls._instance is None:
                    cls._instance = super(TypeCache, cls).__new__(cls)
            finally:
                cls._lock.release()
        return cls._instance

    def cache_type(self, type_name):
        """
        Cache a type.
        
        :param type_name: Type name to cache
        """
        with self._lock:
            # Handle Python 2.7 vs Python 3 module name differences
            if type_name.startswith("builtins"):
                type_name = type_name.replace("builtins", "__builtin__", 1)
            
            self.type_cache.append(type_name)

    def is_type_cache_empty(self):
        self._lock.acquire()
        try:
            return len(self.type_cache) == 0
        finally:
            self._lock.release()

    def is_type_allowed(self, type_to_check):
        self._lock.acquire()
        try:
            if isinstance(type_to_check, types.ModuleType):
                name_to_check = type_to_check.__name__
            else:
                name_to_check = ".".join([type_to_check.__module__, type_to_check.__name__])
            for pattern in self.type_cache:
                if re.match(pattern, name_to_check):
                    return True
            return False
        finally:
            self._lock.release()

    def get_cached_types(self):
        self._lock.acquire()
        try:
            return self.type_cache[:]
        finally:
            self._lock.release()

    def clear_cache(self):
        self._lock.acquire()
        try:
            del self.type_cache[:]
            return 0
        finally:
            self._lock.release()
