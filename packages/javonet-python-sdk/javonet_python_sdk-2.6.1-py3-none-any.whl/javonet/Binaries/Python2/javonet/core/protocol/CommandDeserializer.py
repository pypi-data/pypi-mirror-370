# -*- coding: utf-8 -*-
"""
The CommandDeserializer module implements command deserialization.
"""

from javonet.core.protocol.TypeDeserializer import TypeDeserializer
from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.StringEncodingMode import StringEncodingMode
from javonet.utils.Type import Type


class CommandDeserializer(object):
    """
    Class responsible for command deserialization.
    """
    position = 0
    buffer = []
    command = 0
    buffer_len = 0

    def __init__(self, buffer):
        """
        Initializes a new command deserializer.

        :param buffer: Buffer with data to deserialize
        """
        self.buffer = buffer
        self.buffer_len = len(buffer)
        if self.buffer_len < 11:
            raise ValueError("Buffer too small to contain a command header.")
        self.command = Command(RuntimeName(buffer[0]), CommandType(buffer[10]), [])
        self.position = 11

    def is_at_end(self):
        """
        Checks if the end of buffer has been reached.

        :return: True if end of buffer is reached, False otherwise
        """
        return self.position >= self.buffer_len

    def deserialize(self):
        """
        Deserializes a command.

        :return: Deserialized command
        """
        while not self.is_at_end():
            self.command = self.command.add_arg_to_payload(self.read_object(self.buffer[self.position]))
        return self.command

    def _check_buffer(self, required_size):
        """Checks if there are enough bytes left in the buffer."""
        if self.position + required_size > self.buffer_len:
            raise IndexError("Not enough data in buffer to read next value.")

    def read_object(self, type_num):
        """
        Reads an object from the buffer based on its type.

        :param type_num: Type number
        :return: Read object
        """
        type_value = Type(type_num)
        switch = {
            Type.Command: self.read_command,
            Type.JavonetString: self.read_string,
            Type.JavonetInteger: self.read_int,
            Type.JavonetBoolean: self.read_bool,
            Type.JavonetFloat: self.read_float,
            Type.JavonetByte: self.read_byte,
            Type.JavonetChar: self.read_char,
            Type.JavonetLongLong: self.read_longlong,
            Type.JavonetDouble: self.read_double,
            Type.JavonetUnsignedLongLong: self.read_ullong,
            Type.JavonetUnsignedInteger: self.read_uint,
            Type.JavonetNoneType: self.read_none
        }
        func = switch.get(type_value)
        if func is None:
            raise ValueError("Type not supported: " + str(type_num))
        return func()

    def read_command(self):
        """
        Reads a command from the buffer.

        :return: Read command
        """
        self._check_buffer(7)
        p = self.position
        number_of_elements_in_payload = TypeDeserializer.deserialize_int(self.buffer[p + 1: p + 5])
        runtime = self.buffer[p + 5]
        command_type = self.buffer[p + 6]
        self.position += 7

        payload = []
        for _ in xrange(number_of_elements_in_payload):
            payload.append(self.read_object(self.buffer[self.position]))

        return Command(RuntimeName(runtime), CommandType(command_type), payload)

    def read_string(self):
        """
        Reads a string from the buffer.

        :return: Read string
        """
        self._check_buffer(6)
        p = self.position
        string_encoding_mode = StringEncodingMode(self.buffer[p + 1])
        size = TypeDeserializer.deserialize_int(self.buffer[p + 2:p + 6])
        self.position += 6
        self._check_buffer(size)
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_string(string_encoding_mode, self.buffer[p:p + size])

    def read_int(self):
        size = 4
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_int(self.buffer[p:p + size])

    def read_bool(self):
        size = 1
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_bool(self.buffer[p:p + size])

    def read_float(self):
        size = 4
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_float(self.buffer[p:p + size])

    def read_byte(self):
        size = 1
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_byte(self.buffer[p:p + size])

    def read_char(self):
        size = 1
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_char(self.buffer[p:p + size])

    def read_longlong(self):
        size = 8
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_longlong(self.buffer[p:p + size])

    def read_double(self):
        size = 8
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size

        return TypeDeserializer.deserialize_double(self.buffer[p:p + size])

    def read_ullong(self):
        size = 8
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_ullong(self.buffer[p:p + size])

    def read_uint(self):
        size = 4
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_uint(self.buffer[p:p + size])

    def read_none(self):
        size = 1
        self._check_buffer(size + 2)
        self.position += 2
        p = self.position
        self.position += size
        return TypeDeserializer.deserialize_none(self.buffer[p:p + size])
