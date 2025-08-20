# -*- coding: utf-8 -*-
import re
import types
import threading


class NamespaceCache(object):
    _instance = None
    namespace_cache = list()
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._lock.acquire()
            try:
                if cls._instance is None:
                    cls._instance = super(NamespaceCache, cls).__new__(cls)
            finally:
                cls._lock.release()
        return cls._instance

    def cache_namespace(self, namespace):
        """
        Cache a namespace.
        
        :param namespace: Namespace to cache
        """
        with self._lock:
            # Handle Python 2.7 vs Python 3 module name differences
            if namespace.startswith("builtins"):
                namespace = namespace.replace("builtins", "__builtin__", 1)
            
            self.namespace_cache.append(namespace)

    def is_namespace_cache_empty(self):
        self._lock.acquire()
        try:
            return len(self.namespace_cache) == 0
        finally:
            self._lock.release()

    def is_type_allowed(self, type_to_check):
        self._lock.acquire()
        try:
            for pattern in self.namespace_cache:
                if isinstance(type_to_check, types.ModuleType):
                    if re.match(pattern, type_to_check.__name__):
                        return True
                else:
                    if re.match(pattern, type_to_check.__module__):
                        return True
            return False
        finally:
            self._lock.release()

    def get_cached_namespaces(self):
        self._lock.acquire()
        try:
            return self.namespace_cache[:]
        finally:
            self._lock.release()

    def clear_cache(self):
        self._lock.acquire()
        try:
            del self.namespace_cache[:]
            return 0
        finally:
            self._lock.release()
