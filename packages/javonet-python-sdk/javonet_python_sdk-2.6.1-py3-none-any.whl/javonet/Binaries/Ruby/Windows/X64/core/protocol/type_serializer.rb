require_relative '../../utils/type'
require_relative '../../utils/string_encoding_mode'

class TypeSerializer

  def self.serialize_primitive(payload_item)
    if payload_item.nil?
      return serialize_nil
    elsif [true, false].include? payload_item
      return serialize_bool(payload_item)
    elsif payload_item.is_a? Integer
      if (-2 ** 31..2 ** 31 - 1).include?(payload_item)
        return serialize_int(payload_item)
      elsif (-2 ** 63..2 ** 63 - 1).include?(payload_item)
        return serialize_longlong(payload_item)
      else
        return serialize_ullong(payload_item)
      end
    elsif payload_item.is_a? String
      return serialize_string(payload_item)
    elsif payload_item.is_a? Float
      return serialize_double(payload_item)
    elsif payload_item.is_a?(FalseClass) || payload_item.is_a?(TrueClass)
      return serialize_bool(payload_item)
    else
      raise TypeError, "Unsupported payload item type: #{payload_item.class} for payload item: #{payload_item}."
    end
  end

  def self.serialize_command(command)
    length = int_to_bytes(command.payload.length)
    return [Type::COMMAND] + length + [command.runtime_name, command.command_type]
  end

  def self.serialize_string(string_value)
    encoded_string_list = string_value.bytes
    length = int_to_bytes(encoded_string_list.length)
    return [Type::JAVONET_STRING, StringEncodingMode::UTF8] + length + encoded_string_list
  end

  def self.serialize_int(int_value)
    encoded_int_list = int_to_bytes(int_value)
    length = encoded_int_list.length
    return [Type::JAVONET_INTEGER, length] + encoded_int_list
  end

  def self.serialize_bool(bool_value)
    encoded_bool_list = bool_value ? [1] : [0]
    length = encoded_bool_list.length
    return [Type::JAVONET_BOOLEAN, length] + encoded_bool_list
  end

  def self.serialize_float(float_value)
    encoded_float_list = float_to_bytes(float_value)
    length = encoded_float_list.length
    return [Type::JAVONET_FLOAT, length] + encoded_float_list
  end

  def self.serialize_byte(byte_value)
    encoded_byte_list = [byte_value & 0xFF]
    length = encoded_byte_list.length
    return [Type::JAVONET_BYTE, length] + encoded_byte_list
  end

  def self.serialize_char(char_value)
    encoded_char_list = [char_value & 0xFF]
    length = encoded_char_list.length
    return [Type::JAVONET_CHAR, length] + encoded_char_list
  end

  def self.serialize_longlong(longlong_value)
    encoded_longlong_list = longlong_to_bytes(longlong_value)
    length = encoded_longlong_list.length
    return [Type::JAVONET_LONG_LONG, length] + encoded_longlong_list
  end

  def self.serialize_double(double_value)
    encoded_double_list = double_to_bytes(double_value)
    length = encoded_double_list.length
    return [Type::JAVONET_DOUBLE, length] + encoded_double_list
  end

  def self.serialize_uint(uint_value)
    encoded_uint_list = uint_to_bytes(uint_value)
    length = encoded_uint_list.length
    return [Type::JAVONET_UNSIGNED_INTEGER, length] + encoded_uint_list
  end

  def self.serialize_ullong(ullong_value)
    encoded_ullong_list = ullong_to_bytes(ullong_value)
    length = encoded_ullong_list.length
    return [Type::JAVONET_UNSIGNED_LONG_LONG, length] + encoded_ullong_list
  end

  def self.serialize_nil
    return [Type::JAVONET_NULL, 1, 0]
  end

  # Helper methods for byte conversion
  def self.int_to_bytes(value)
    # Convert to 4-byte (32-bit) integer, little-endian
    [
      value & 0xFF,
      (value >> 8) & 0xFF,
      (value >> 16) & 0xFF,
      (value >> 24) & 0xFF
    ]
  end

  def self.uint_to_bytes(value)
    # Convert to 4-byte unsigned integer, little-endian
    [
      value & 0xFF,
      (value >> 8) & 0xFF,
      (value >> 16) & 0xFF,
      (value >> 24) & 0xFF
    ]
  end

  def self.longlong_to_bytes(value)
    # Convert to 8-byte (64-bit) integer, little-endian
    [
      value & 0xFF,
      (value >> 8) & 0xFF,
      (value >> 16) & 0xFF,
      (value >> 24) & 0xFF,
      (value >> 32) & 0xFF,
      (value >> 40) & 0xFF,
      (value >> 48) & 0xFF,
      (value >> 56) & 0xFF
    ]
  end

  def self.ullong_to_bytes(value)
    # Convert to 8-byte unsigned long long, little-endian
    [
      value & 0xFF,
      (value >> 8) & 0xFF,
      (value >> 16) & 0xFF,
      (value >> 24) & 0xFF,
      (value >> 32) & 0xFF,
      (value >> 40) & 0xFF,
      (value >> 48) & 0xFF,
      (value >> 56) & 0xFF
    ]
  end

  def self.float_to_bytes(value)
    # IEEE 754 single-precision binary floating-point format (32-bit)
    # Manual implementation without using pack
    bits = 0

    if value == 0
      # Zero is a special case
      return [0, 0, 0, 0]
    elsif value.nan?
      # NaN is another special case
      bits = 0x7FC00000
    elsif value.infinite?
      # Handle infinity
      bits = value > 0 ? 0x7F800000 : 0xFF800000
    else
      # Regular number
      sign = value < 0 ? 1 : 0
      value = value.abs

      # Get exponent and fraction
      exponent = Math.log2(value).floor
      fraction = value / (2.0**exponent) - 1.0

      # Normalize exponent for IEEE 754 bias
      biased_exponent = exponent + 127

      # Clamp exponent to valid range
      if biased_exponent <= 0
        # Denormalized values
        biased_exponent = 0
        fraction = value / (2.0**(-126))
      elsif biased_exponent >= 255
        # Overflow, return infinity
        biased_exponent = 255
        fraction = 0
      end

      # Assemble the bits
      fraction_bits = (fraction * 0x800000).round & 0x7FFFFF
      bits = (sign << 31) | (biased_exponent << 23) | fraction_bits
    end

    # Convert to bytes (little-endian)
    [
      bits & 0xFF,
      (bits >> 8) & 0xFF,
      (bits >> 16) & 0xFF,
      (bits >> 24) & 0xFF
    ]
  end

  def self.double_to_bytes(value)
    # IEEE 754 double-precision binary floating-point format (64-bit)
    # Manual implementation without using pack
    bits_low = 0
    bits_high = 0

    if value == 0
      # Zero is a special case
      return [0, 0, 0, 0, 0, 0, 0, 0]
    elsif value.nan?
      # NaN is another special case
      bits_high = 0x7FF80000
      bits_low = 0
    elsif value.infinite?
      # Handle infinity
      bits_high = value > 0 ? 0x7FF00000 : 0xFFF00000
      bits_low = 0
    else
      # Regular number
      sign = value < 0 ? 1 : 0
      value = value.abs

      # Get exponent and fraction
      exponent = Math.log2(value).floor
      fraction = value / (2.0**exponent) - 1.0

      # Normalize exponent for IEEE 754 bias
      biased_exponent = exponent + 1023

      # Clamp exponent to valid range
      if biased_exponent <= 0
        # Denormalized values
        biased_exponent = 0
        fraction = value / (2.0**(-1022))
      elsif biased_exponent >= 2047
        # Overflow, return infinity
        biased_exponent = 2047
        fraction = 0
      end

      # Assemble the bits
      # Convert a fraction to 52-bit integer
      fraction_bits = (fraction * 0x10000000000000).round

      # Split into high and low 32-bit words
      bits_high = (sign << 31) | (biased_exponent << 20) | ((fraction_bits >> 32) & 0xFFFFF)
      bits_low = fraction_bits & 0xFFFFFFFF
    end

    # Convert to bytes (little-endian)
    [
      bits_low & 0xFF,
      (bits_low >> 8) & 0xFF,
      (bits_low >> 16) & 0xFF,
      (bits_low >> 24) & 0xFF,
      bits_high & 0xFF,
      (bits_high >> 8) & 0xFF,
      (bits_high >> 16) & 0xFF,
      (bits_high >> 24) & 0xFF
    ]
  end
end
