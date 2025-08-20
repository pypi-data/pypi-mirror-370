# -*- coding: utf-8 -*-
import uuid
import threading
from javonet.utils.CommandType import CommandType


class ReferencesCache(object):
    _instance = None
    references_cache = dict()
    _lock = threading.Lock()

    def __new__(cls):
        cls._lock.acquire()
        try:
            if cls._instance is None:
                cls._instance = super(ReferencesCache, cls).__new__(cls)
        finally:
            cls._lock.release()
        return cls._instance

    def cache_reference(self, object_reference):
        self._lock.acquire()
        try:
            uuid_ = str(uuid.uuid4())
            self.references_cache[uuid_] = object_reference
            return uuid_
        finally:
            self._lock.release()

    def resolve_reference(self, command):
        try:
            command_val = command.command_type.value
            ref_val = CommandType.Reference.value
        except AttributeError:
            command_val = command.command_type
            ref_val = CommandType.Reference
        if command_val != ref_val:
            raise Exception("Trying to dereference Python command with command_type: " + str(command.command_type))
        self._lock.acquire()
        try:
            try:
                return self.references_cache[command.payload[0]]
            except KeyError:
                raise Exception("Object not found in references")
        finally:
            self._lock.release()

    def delete_reference(self, reference_guid):
        self._lock.acquire()
        try:
            try:
                del self.references_cache[reference_guid]
                return 0
            except KeyError:
                raise Exception("Object not found in references")
        finally:
            self._lock.release()