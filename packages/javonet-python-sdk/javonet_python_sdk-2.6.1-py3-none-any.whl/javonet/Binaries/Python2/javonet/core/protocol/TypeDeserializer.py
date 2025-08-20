"""
The TypeDeserializer module implements type deserialization.
"""

import struct

from javonet.utils.Command import Command
from javonet.utils.CommandType import CommandType
from javonet.utils.RuntimeName import RuntimeName
from javonet.utils.StringEncodingMode import StringEncodingMode


class TypeDeserializer(object):
    """
    Class responsible for type deserialization.
    """

    @staticmethod
    def deserialize_command(encoded_command):
        """
        Deserializes a command.

        :param encoded_command: Encoded command
        :return: Deserialized command
        """
        return Command(RuntimeName(encoded_command[0]), CommandType(encoded_command[1]), [])

    @staticmethod
    def deserialize_string(string_encoding_mode, encoded_string):
        """
        Deserializes a string.

        :param string_encoding_mode: String encoding mode
        :param encoded_string: Encoded string
        :return: Deserialized string
        :raises: IndexError if string encoding mode is out of range
        """
        # Handle the case when string_encoding_mode is an integer or has a different value
        if hasattr(string_encoding_mode, 'value'):
            mode_value = string_encoding_mode.value
        else:
            mode_value = string_encoding_mode

        if mode_value == 0:  # ASCII
            return bytearray(encoded_string).decode('ascii')
        if mode_value == 1:  # UTF8
            return bytearray(encoded_string).decode('utf-8')
        if mode_value == 2:  # UTF16
            return bytearray(encoded_string).decode('utf-16')
        if mode_value == 3:  # UTF32
            return bytearray(encoded_string).decode('utf-32')

        # Default to UTF-8 for unknown encoding modes
        return bytearray(encoded_string).decode('utf-8')

    @staticmethod
    def deserialize_int(encoded_int):
        """
        Deserializes an integer.

        :param encoded_int: Encoded integer
        :return: Deserialized integer
        """
        return struct.unpack("<i", bytearray(encoded_int))[0]

    @staticmethod
    def deserialize_bool(encoded_bool):
        """
        Deserializes a boolean.

        :param encoded_bool: Encoded boolean
        :return: Deserialized boolean
        """
        return struct.unpack("<?", bytearray(encoded_bool))[0]

    @staticmethod
    def deserialize_float(encoded_float):
        """
        Deserializes a float.

        :param encoded_float: Encoded float
        :return: Deserialized float
        """
        return struct.unpack("<f", bytearray(encoded_float))[0]

    @staticmethod
    def deserialize_byte(encoded_byte):
        """
        Deserializes a byte.

        :param encoded_byte: Encoded byte
        :return: Deserialized byte
        """
        return struct.unpack("<B", bytearray(encoded_byte))[0]

    @staticmethod
    def deserialize_char(encoded_char):
        """
        Deserializes a character.

        :param encoded_char: Encoded character
        :return: Deserialized character
        """
        return struct.unpack("<b", bytearray(encoded_char))[0]

    @staticmethod
    def deserialize_longlong(encoded_longlong):
        """
        Deserializes a long long.

        :param encoded_longlong: Encoded long long
        :return: Deserialized long long
        """
        return struct.unpack("<q", bytearray(encoded_longlong))[0]

    @staticmethod
    def deserialize_double(encoded_double):
        """
        Deserializes a double.

        :param encoded_double: Encoded double
        :return: Deserialized double
        """
        return struct.unpack("<d", bytearray(encoded_double))[0]

    @staticmethod
    def deserialize_ullong(encoded_unsigned_longlong):
        """
        Deserializes an unsigned long long.

        :param encoded_unsigned_longlong: Encoded unsigned long long
        :return: Deserialized unsigned long long
        """
        return struct.unpack("<Q", bytearray(encoded_unsigned_longlong))[0]

    @staticmethod
    def deserialize_uint(encoded_unsigned_int):
        """
        Deserializes an unsigned integer.

        :param encoded_unsigned_int: Encoded unsigned integer
        :return: Deserialized unsigned integer
        """
        return struct.unpack("<I", bytearray(encoded_unsigned_int))[0]

    @staticmethod
    def deserialize_none(encoded_none):
        """
        Deserializes a None value.

        :param encoded_none: Encoded None value
        :return: None
        """
        return None 