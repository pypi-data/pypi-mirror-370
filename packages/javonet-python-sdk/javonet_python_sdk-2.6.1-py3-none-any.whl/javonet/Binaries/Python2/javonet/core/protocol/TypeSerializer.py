"""
The TypeSerializer module implements type serialization.
"""

import struct

from javonet.utils.Type import Type
from javonet.utils.StringEncodingMode import StringEncodingMode


class TypeSerializer(object):
    """
    Class responsible for type serialization.
    """

    @staticmethod
    def serialize_primitive(payload_item):
        """
        Serializes a primitive value.

        :param payload_item: Value to serialize
        :return: Serialized value
        :raises: Exception if type is not supported
        """
        if payload_item is None:
            return TypeSerializer.serialize_none()
        if isinstance(payload_item, bool):
            return TypeSerializer.serialize_bool(payload_item)
        elif isinstance(payload_item, (int, long)):
            # In Python 2.7, we need to avoid using range() for large numbers
            if -2**31 <= payload_item < 2**31:
                return TypeSerializer.serialize_int(payload_item)
            elif -2**63 <= payload_item < 2**63:
                return TypeSerializer.serialize_longlong(payload_item)
            else:
                return TypeSerializer.serialize_ullong(payload_item)
        elif isinstance(payload_item, float):
            return TypeSerializer.serialize_double(payload_item)
        elif isinstance(payload_item, (str, unicode)):
            return TypeSerializer.serialize_string(payload_item)
        elif isinstance(payload_item, bytearray):
            return TypeSerializer.serialize_byte(payload_item)
        else:
            raise TypeError("Unsupported payload item type: {} for payload item: {}.".format(type(payload_item), payload_item))


    @staticmethod
    def serialize_command(command):
        """
        Serializes a command.

        :param command: Command to serialize
        :return: Serialized command
        """
        length = list(bytearray(struct.pack("<i", len(command.payload))))
        return [Type.Command.value] + length + [command.runtime_name.value, command.command_type.value]

    @staticmethod
    def serialize_string(string_value):
        """
        Serializes a string.

        :param string_value: String to serialize
        :return: Serialized string
        """
        if isinstance(string_value, unicode):
            encoded_string_list = list(bytearray(string_value.encode('utf-8')))
        else:
            encoded_string_list = list(bytearray(string_value))
        length = list(bytearray(struct.pack("<i", len(encoded_string_list))))
        return [Type.JavonetString.value] + [StringEncodingMode.UTF8.value] + length + encoded_string_list

    @staticmethod
    def serialize_int(int_value):
        """
        Serializes an integer.

        :param int_value: Integer to serialize
        :return: Serialized integer
        """
        encoded_int_list = list(bytearray(struct.pack("<i", int_value)))
        length = len(encoded_int_list)
        return [Type.JavonetInteger.value, length] + encoded_int_list

    @staticmethod
    def serialize_bool(bool_value):
        """
        Serializes a boolean.

        :param bool_value: Boolean to serialize
        :return: Serialized boolean
        """
        encoded_bool_list = list(bytearray(struct.pack("?", bool_value)))
        length = len(encoded_bool_list)
        return [Type.JavonetBoolean.value, length] + encoded_bool_list

    @staticmethod
    def serialize_float(float_value):
        """
        Serializes a float.

        :param float_value: Float to serialize
        :return: Serialized float
        """
        encoded_float_list = list(bytearray(struct.pack("<f", float_value)))
        length = len(encoded_float_list)
        return [Type.JavonetFloat.value, length] + encoded_float_list

    @staticmethod
    def serialize_byte(bytes_value):
        """
        Serializes a byte.

        :param bytes_value: Byte to serialize
        :return: Serialized byte
        """
        encoded_byte_list = list(bytearray(struct.pack("<B", bytes_value)))
        length = len(encoded_byte_list)
        return [Type.JavonetByte.value, length] + encoded_byte_list

    @staticmethod
    def serialize_char(char_value):
        """
        Serializes a character.

        :param char_value: Character to serialize
        :return: Serialized character
        """
        encoded_char_list = list(bytearray(struct.pack("<b", char_value)))
        length = len(encoded_char_list)
        return [Type.JavonetChar.value, length] + encoded_char_list

    @staticmethod
    def serialize_longlong(longlong_value):
        """
        Serializes a long long.

        :param longlong_value: Long long to serialize
        :return: Serialized long long
        """
        encoded_longlong_list = list(bytearray(struct.pack("<q", longlong_value)))
        length = len(encoded_longlong_list)
        return [Type.JavonetLongLong.value, length] + encoded_longlong_list

    @staticmethod
    def serialize_double(double_value):
        """
        Serializes a double.

        :param double_value: Double to serialize
        :return: Serialized double
        """
        encoded_double_list = list(bytearray(struct.pack("<d", double_value)))
        length = len(encoded_double_list)
        return [Type.JavonetDouble.value, length] + encoded_double_list

    @staticmethod
    def serialize_ullong(unsigned_longlong_value):
        """
        Serializes an unsigned long long.

        :param unsigned_longlong_value: Unsigned long long to serialize
        :return: Serialized unsigned long long
        """
        encoded_unsignedlonglong_list = list(bytearray(struct.pack("<Q", unsigned_longlong_value)))
        length = len(encoded_unsignedlonglong_list)
        return [Type.JavonetUnsignedLongLong.value, length] + encoded_unsignedlonglong_list

    @staticmethod
    def serialize_uint(unsigned_int_value):
        """
        Serializes an unsigned integer.

        :param unsigned_int_value: Unsigned integer to serialize
        :return: Serialized unsigned integer
        """
        encoded_unsigned_int_list = list(bytearray(struct.pack("<I", unsigned_int_value)))
        length = len(encoded_unsigned_int_list)
        return [Type.JavonetUnsignedInteger.value, length] + encoded_unsigned_int_list

    @staticmethod
    def serialize_none():
        """
        Serializes a None value.

        :return: Serialized None value
        """
        return [Type.JavonetNoneType.value, 1, 0] 